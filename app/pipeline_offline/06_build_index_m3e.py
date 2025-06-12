#!/usr/bin/env python3
"""
Step 6 (m3e version): build centroids, FAISS index, and
semantic keywords per cluster.
"""
import numpy as np, pickle, json, faiss, pathlib, tqdm, re, itertools, collections
from sentence_transformers import SentenceTransformer, util
import torch, networkx as nx

# ───────── 경로 ─────────
EMB_PATH   = pathlib.Path("indices/paper_embed.npy")
LABEL_PATH = pathlib.Path("indices/cluster_labels.npy")
PID_MAP    = pathlib.Path("indices/pid2idx.pkl")
GRAPH_PATH = pathlib.Path("indices/graph_raw.gpickle")

OUT_CENT   = pathlib.Path("indices/cluster_centroids.npy")
OUT_INDEX  = pathlib.Path("indices/cluster.index")
OUT_META   = pathlib.Path("indices/cluster_meta.json")

# ───────── 로드 ─────────
emb      = np.load(EMB_PATH).astype("float32")           # (N,512)
labels   = np.load(LABEL_PATH)
pid2idx  = pickle.load(PID_MAP.open("rb"))
with open(GRAPH_PATH, "rb") as f:
    G: nx.DiGraph = pickle.load(f)

# cluster → pids
clusters = {}
for pid, idx in pid2idx.items():
    clusters.setdefault(int(labels[idx]), []).append(pid)

# ───────── m3e 모델 ─────────
model = SentenceTransformer('moka-ai/m3e-base', device="cuda:0")
TOKEN  = re.compile(r"[a-zA-Z가-힣0-9\-]{2,}")   # 2+ 글자 토큰

def _abs(pid):
    """abstract 문자열 안전 추출"""
    a = G.nodes[pid].get("abstract", "")
    if isinstance(a, list):
        a = " ".join(map(str, a))
    return str(a)

def extract_ngram(txt, max_n=3):
    ws = TOKEN.findall(txt.lower())
    for n in range(1, max_n + 1):
        for i in range(len(ws) - n + 1):
            yield " ".join(ws[i:i + n])

def semantic_keywords(pids, centroid_txt, top_n=8):
    docs = [_abs(p) for p in pids]
    # 후보 n-gram 수집 & 빈도 필터
    cand = (c for d in docs for c in extract_ngram(d))
    counts = collections.Counter(itertools.islice(cand, 0, 40000))
    cand = [w for w, c in counts.items() if c >= 2 and len(w) <= 40][:10000]
    if not cand:
        return []
    # 임베딩 & cosine sim
    emb_cand = model.encode(cand, batch_size=256, normalize_embeddings=True)
    sim = util.cos_sim(torch.tensor(centroid_txt), emb_cand)[0].cpu().numpy()
    return [c for c, _ in sorted(zip(cand, sim), key=lambda x: x[1], reverse=True)[:top_n]]

# ───────── centroid + keywords ─────────
centroids, meta = [], {}
for cid, pids in tqdm.tqdm(clusters.items(), desc="centroid/keywords"):
    idxs = [pid2idx[p] for p in pids]
    cent = emb[idxs].mean(0)                       # (512,)
    centroids.append(cent.astype("float32"))

    # 텍스트 384-d 부분만 사용하여 키워드 추출
    cent_txt = cent[:-128] / (np.linalg.norm(cent[:-128]) + 1e-9)
    kws = semantic_keywords(pids, cent_txt)

    meta[cid] = {"size": len(pids), "keywords": kws}

# ───────── 저장 ─────────
cent = np.vstack(centroids).astype("float32")
np.save(OUT_CENT, cent)

index = faiss.IndexFlatIP(cent.shape[1])
index.add(cent)
faiss.write_index(index, str(OUT_INDEX))

json.dump(meta, OUT_META.open("w"))
print("✓ Saved:", OUT_CENT, OUT_INDEX, OUT_META)
