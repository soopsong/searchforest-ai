#!/usr/bin/env python3
"""
Step 6:  build cluster centroids, FAISS index, and keyword meta
Inputs
  • indices/paper_embed.npy      – (N, 512) float32
  • indices/cluster_labels.npy   – (N,)     int32
  • indices/pid2idx.pkl          – {paper_id: row_idx}
  • indices/text_emb.npz         – paper_id → 384-d text vec (for TF-IDF)
Outputs
  • indices/cluster_centroids.npy    – (C, 512) float32
  • indices/cluster.index            – FAISS IndexFlatIP on centroids
  • indices/cluster_meta.json        – {cid: {size, keywords}}
"""
import numpy as np, pickle, json, faiss, pathlib, tqdm
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer, util
import itertools, re, collections

EMB_PATH   = pathlib.Path("indices/paper_embed.npy")
LABEL_PATH = pathlib.Path("indices/cluster_labels.npy")
PID_MAP    = pathlib.Path("indices/pid2idx.pkl")
TEXT_PATH  = pathlib.Path("indices/text_emb.npz")

OUT_CENT   = pathlib.Path("indices/cluster_centroids.npy")
OUT_INDEX  = pathlib.Path("indices/cluster.index")
OUT_META   = pathlib.Path("indices/cluster_meta.json")

# ── load ───────────────────────────────────────────────
emb     = np.load(EMB_PATH)                     # (N, 512)
labels  = np.load(LABEL_PATH)                   # (N,)
pid2idx = pickle.load(PID_MAP.open("rb"))
text_npz= np.load(TEXT_PATH)

print("🔹 group by cluster …")
clusters = {}
for pid, idx in pid2idx.items():
    cid = int(labels[idx])
    clusters.setdefault(cid, []).append(pid)

# ── centroid & keywords ────────────────────────────────
centroids, meta = [], {}
tfidf = TfidfVectorizer(stop_words="english", max_features=40_000)

for cid, pids in tqdm.tqdm(clusters.items(), desc="centroid/keywords"):
    idxs = [pid2idx[p] for p in pids]
    cent = emb[idxs].mean(0, dtype="float32")
    centroids.append(cent)

    # 키워드: 클러스터 논문의 abstract 텍스트로 TF-IDF
    docs = [text_npz[p] for p in pids if p in text_npz]
    kws  = []
    if docs:
        X = tfidf.fit_transform([v.tobytes().decode("utf-8","ignore")
                                 for v in docs])
        sums = np.asarray(X.sum(0)).ravel()
        order= sums.argsort()[::-1][:20]
        kws  = tfidf.get_feature_names_out()[order].tolist()

    meta[cid] = {"size": len(pids), "keywords": kws}

# ── save ───────────────────────────────────────────────
centroids = np.vstack(centroids).astype("float32")
np.save(OUT_CENT, centroids)

index = faiss.IndexFlatIP(centroids.shape[1])
index.add(centroids)
faiss.write_index(index, str(OUT_INDEX))

json.dump(meta, OUT_META.open("w"))
print("✓ centroids:", centroids.shape,
      "/ index & meta saved to indices/")
