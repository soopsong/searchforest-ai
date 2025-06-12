#!/usr/bin/env python3
# runtime/graph_builder.py
import pickle, re, networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np, tqdm

# 1) citation 그래프 + abstract 로드 ------------------------------------------------
with open("indices/graph_raw.gpickle", "rb") as f:
    G: nx.DiGraph = pickle.load(f)           # ↔ DiGraph 그대로 복구

# 2) 유틸 -------------------------------------------------------------------------
TOKEN_RE = re.compile(r"^[a-zA-Z]{2,}$")     # 영문 ≥3 글자 토큰만

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

# 3) build_tree -------------------------------------------------------------------
_abs_cache = {}
def get_abs(pid):
    if pid not in _abs_cache:
        _abs_cache[pid] = _as_text(G.nodes[pid].get("abstract", "")).lower()
    return _abs_cache[pid]

def build_tree(root_kw: str, pids_lvl0, cluster2pids, depth: int = 2):
    """
    • root_kw      : 트리 루트 키워드(클러스터 대표)
    • pids_lvl0    : 해당 클러스터 논문 ID 리스트
    • depth        : 2(기본) → hop-1 / hop-2 생성
    반환값         : dict(JSON-serializable)
    """
    tree = {"root": root_kw, "children": []}

    for kw1 in top_keywords(pids_lvl0, n=6):
        hop1 = [p for p in pids_lvl0 if contains_kw(get_abs(p), kw1)]
        node_lvl1 = {"kw": kw1, "pids": hop1, "children": []}

        if depth > 1:
            # hop-1 논문의 reference 논문 모으기
            refs = [r for p in hop1 if G.has_node(p) for r in G.successors(p)]
            for kw2 in top_keywords(refs, n=4):
                hop2 = [p for p in refs if contains_kw(get_abs(p), kw2)]
                node_lvl1["children"].append({"kw": kw2, "pids": hop2})

        tree["children"].append(node_lvl1)

    return tree
