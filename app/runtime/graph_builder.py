#!/usr/bin/env python3
# runtime/graph_builder.py
import pickle, re, networkx as nx
import pathlib 
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers.util import cos_sim
import numpy as np, tqdm
from sentence_transformers import SentenceTransformer, util
import torch
from runtime.cluster_searcher import meta, cluster2pids   # ← meta 와 함께 추가로 import




# ── 전역 설정 ───────────────────────────────────────────
α, β, γ = 0.4, 0.4, 0.2         # (query, parentKw, TF-IDF) 가중치
MMR_LAMBDA = 0.6
model = SentenceTransformer("moka-ai/m3e-base", device="cuda:0")

def tfidf_score(kw, tfidf_dict):
    """클러스터 TF-IDF 합 딕셔너리에서 점수 조회 (없으면 0)"""
    return tfidf_dict.get(kw, 0.0)
# graph_builder.py  ── 기존 select_kw 대체
def select_kw_scored(query_kw: str,
                     candidate_kws: list[str],
                     tfidf_dict: dict[str, float],
                     k: int = 5):
    """
    반환값: [(kw, score), …]  (score는 0~1 정도의 실수)
    """
    q_emb      = model.encode([query_kw], normalize_embeddings=True)[0]
    cand_embs  = model.encode(candidate_kws, normalize_embeddings=True)

    scored = []
    for kw, e in zip(candidate_kws, cand_embs):
        sc = (α * util.cos_sim(q_emb, e).item() +
              β * util.cos_sim(q_emb, e).item() +     # parent==query
              γ * tfidf_score(kw, tfidf_dict))
        scored.append([sc, kw, e])

    # ── MMR 다양화 ────────────────────────────────
    selected, selected_embs = [], []
    while scored and len(selected) < k:
        scored.sort(reverse=True)          # sc 내림차순
        best_sc, best_kw, best_emb = scored.pop(0)
        selected.append((best_kw, best_sc))
        selected_embs.append(best_emb)

        # diversity 보정
        new_scored = []
        for sc, kw, e in scored:
            div = max(util.cos_sim(e, se).item() for se in selected_embs)
            new_scored.append([sc - MMR_LAMBDA * div, kw, e])
        scored = new_scored

    return selected            # [(kw, score), …]






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

def build_tree(root_kw: str, cid: int, depth: int = 1):
    c_meta = meta[str(cid)]
    cand   = c_meta["keywords"]
    tfidf_dict = dict(zip(
        c_meta["keywords"],
        c_meta.get("tfidf_sums", [])
    ))
    pids_lvl0 = cluster2pids[cid]

    tree = {"id": root_kw, "value": 1.0, "children": []}

    # ── depth-1  (최대 3개) ──────────────────────
    for kw1, sc1 in select_kw_scored(root_kw, cand, tfidf_dict, k=3):
        kw1_emb = model.encode([kw1], normalize_embeddings=True)[0]

        hop1 = [
            p for p in pids_lvl0
            if (emb := get_abs_emb(p)) is not None
            and util.cos_sim(kw1_emb, emb).item() > COS_TH1
        ]

        node1 = {
            "id":      kw1,
            "value":   round(sc1, 4),
            "pids":    hop1,          # 필요 없으면 제거
        }

        # ── depth-2 : parent=kw1, 최대 3개 ───────
        if depth > 1:
            for kw2, sc2 in select_kw_scored(kw1, cand, tfidf_dict, k=3):
                node1["children"].append({
                    "id":    kw2,
                    "value": round(sc2, 4),
                })

        tree["children"].append(node1)

    return tree
