#!/usr/bin/env python3
# runtime/graph_builder.py
import pickle, re, networkx as nx
import pathlib 
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers.util import cos_sim
import numpy as np, tqdm
from sentence_transformers import SentenceTransformer, util
import torch

# 1) citation 그래프 + abstract 로드 ------------------------------------------------
with open("indices/graph_raw.gpickle", "rb") as f:
    G: nx.DiGraph = pickle.load(f)           # ↔ DiGraph 그대로 복구

# 2) 유틸 -------------------------------------------------------------------------
TOKEN_RE = re.compile(r"^[a-zA-Z]{2,}$")     # 영문 ≥3 글자 토큰만

# (1) 키워드/문장 임베딩 모델 – m3e 를 그대로 재사용
kw_model = SentenceTransformer("moka-ai/m3e-base", device="cuda:0")

# (2) 논문 abstract 임베딩: 02_embed_text.py 에서 저장한 NPZ 재사용
TEXT_EMB_NPZ = pathlib.Path("indices/text_emb.npz")
text_npz = np.load(TEXT_EMB_NPZ)                # key = paper_id → (384,)


def get_abs_emb(pid: str) -> torch.Tensor:
    """저장된 384-d 벡터를 torch 형태로 반환 (정규화 포함)"""
    if pid not in text_npz:
        return None
    v = text_npz[pid].astype("float32")
    v /= np.linalg.norm(v) + 1e-9
    return torch.from_numpy(v)


# ──────────────────────────────────────────────────────────
# 1) 안전한 키워드 추출 함수 (빈 vocab 방어 포함)
# ----------------------------------------------------------
def safe_top_keywords(pids, n=8):
    docs = [_as_text(G.nodes[p].get("abstract", "")).lower()
            for p in pids if G.has_node(p)]
    if not docs:
        return []
    try:
        X = tfidf.fit_transform(docs)
        if X.shape[1] == 0:
            raise ValueError
        sums = np.asarray(X.sum(0)).ravel()
        kws  = tfidf.get_feature_names_out()
        return [kws[i] for i in sums.argsort()[::-1][:n]]
    except ValueError:
        from collections import Counter
        words = Counter(w for d in docs for w in d.split() if len(w) > 2)
        return [w for w,_ in words.most_common(n)]

def _as_text(x):
    if x is None:
        return ""
    if isinstance(x, list):
        return " ".join(map(str, x))
    return str(x)

def contains_kw(abs_txt: str, kw: str) -> bool:
    """word-boundary 포함 (소문자 비교)"""
    return re.search(rf"\b{re.escape(kw.lower())}\b", abs_txt) is not None

tfidf = TfidfVectorizer(
    stop_words="english",
    token_pattern=r"(?u)\b[a-zA-Z]{2,}\b",   # 2글자↑ 영문 단어
    max_features=40_000,
)

def top_keywords(pids, n=8):
    docs = [_as_text(G.nodes[p].get("abstract", "")).lower()
            for p in pids if G.has_node(p)]
    if not docs:
        return []
    try:
        X = tfidf.fit_transform(docs)
    except ValueError:         # empty vocabulary
        return []              # ← 키워드 없음으로 처리

    scores = np.asarray(X.sum(0)).ravel()
    kws = tfidf.get_feature_names_out()
    good = [kws[i] for i in scores.argsort()[::-1]
            if TOKEN_RE.match(kws[i])][:n]
    return good

    

# ──────────────────────────────────────────────────────────
# 2) build_tree – hop-1/2 선택 로직 수정
# ----------------------------------------------------------
COS_TH1 = 0.30   # hop-1 임계값
COS_TH2 = 0.25   # hop-2 임계값

N_LVL1 = 3      # 1-depth(kw1) 최대 5개
N_LVL2 = 0   # 더 깊이 안 내려감

def build_tree(root_kw: str, pids_lvl0, cluster2pids, depth: int = 2):
    """
    • root_kw      : 트리 루트 키워드(클러스터 대표)
    • pids_lvl0    : 해당 클러스터 논문 ID 리스트
    • depth        : 2(기본) → hop-1 / hop-2 생성
    반환값         : dict(JSON-serializable)
    """
    tree = {"root": root_kw, "children": []}

    # 1-depth (hop-1)
    kw1_list = safe_top_keywords(pids_lvl0, n=N_LVL1*2)[:N_LVL1]   # 후보 넉넉히 뽑고 5개 자르기
    for kw1 in kw1_list:
        kw1_emb = kw_model.encode([kw1], normalize_embeddings=True)[0]

        hop1 = [
            p for p in pids_lvl0
            if (emb := get_abs_emb(p)) is not None
            and util.cos_sim(kw1_emb, emb).item() > COS_TH1
        ]

        node_lvl1 = {"kw": kw1, "pids": hop1, "children": []}

        # 2-depth (hop-2)
        if depth > 1 and hop1:
            succ = [r for p in hop1 for r in G.successors(p)]
            pred = [r for p in hop1 for r in G.predecessors(p)]
            refs = [r for r in succ + pred if G.nodes[r].get("abstract")]
            if len(refs) < 5:      # fallback
                refs = hop1

            seen = set()
            for kw2 in safe_top_keywords(refs, n=10):
                if kw2 == kw1 or kw2 in seen:
                    continue
                seen.add(kw2)
                kw2_emb = kw_model.encode([kw2], normalize_embeddings=True)[0]
                hop2 = [
                    p for p in refs
                    if (emb := get_abs_emb(p)) is not None
                    and util.cos_sim(kw2_emb, emb).item() > COS_TH2
                ]
                node_lvl1["children"].append({"kw": kw2, "pids": hop2})
                if len(node_lvl1["children"]) == N_LVL2:   # 3개까지만
                    break

        tree["children"].append(node_lvl1)
        if len(tree["children"]) == N_LVL1:                # 5개까지만
            break

    return tree