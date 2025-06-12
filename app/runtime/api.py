# runtime/api.py
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn, json

from cluster_searcher import search_clusters, cluster2pids, meta
from graph_builder    import build_tree

from graph_builder import build_tree   # ← 새 함수 import

app = FastAPI(title="SearchForest-AI Recommend API")

# ── Pydantic 스키마 ──────────────────────────────────────────
class SubNode(BaseModel):
    kw:    str
    pids:  list[str]

class ClusterNode(BaseModel):
    kw:     str          # 클러스터 대표 키워드
    sim:    float
    children: list[SubNode]

class RecResponse(BaseModel):
    query: str
    results: dict        # root 트리 전체

# ── recommend ───────────────────────────────────────────────
@app.get("/recommend", response_model=RecResponse)
def recommend(
    query: str = Query(..., description="검색 쿼리"),
    top_k: int = Query(5, gt=1, le=10)          # default 5
):
    # 1) 쿼리 기준 top-k 클러스터
    hits = search_clusters(query, top_k)

    root = {"root": query, "children": []}

    for cid, sim in hits:
        # depth-1 : 클러스터 대표 키워드
        kw_root = meta[str(cid)]["keywords"][0] if meta[str(cid)]["keywords"] else f"cluster{cid}"

        # depth-2 : 클러스터 내부 서브 키워드 ≤ 3개 (build_tree 내부 N_LVL1=3 설정)
        sub_tree = build_tree(
            root_kw      = kw_root,
            pids_lvl0    = cluster2pids[cid],
            cluster2pids = cluster2pids,
            depth        = 2                # 1-depth(kw_root) → 2-depth(서브키워드)
        )
        # build_tree 반환 형식 맞추기
        children_lvl2 = [
            {"kw": n["kw"], "pids": n["pids"]} for n in sub_tree["children"]
        ]

        root["children"].append({
            "kw": kw_root,
            "sim": round(sim, 4),
            "children": children_lvl2
        })

    return {"query": query, "results": root}

# 로컬 실행용
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)