# runtime/api.py
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn, json

from runtime.cluster_searcher import search_clusters, cluster2pids, meta
from runtime.graph_builder    import build_tree


app = FastAPI(title="SearchForest-AI Recommend API")


class InferenceRequest(BaseModel):
    text: str



# ── Pydantic 스키마 ──────────────────────────────────────────
class SubNode(BaseModel):
    kw:    str
    pids:  list[str]

class ClusterNode(BaseModel):
    kw:     str          # 클러스터 대표 키워드
    sim:    float
    children: list[SubNode]

class RecResponse(BaseModel):
    results: dict        # root 트리 전체


# ── recommend ───────────────────────────────────────────────
@app.get("/inference", response_model=RecResponse)
def recommend(
    query: str = Query(..., description="검색 쿼리"),
    top_k: int = Query(10, gt=1, le=10)          # default 10
):
    # 1) 쿼리 기준 top-k 클러스터
    hits = search_clusters(query, top_k)

    root = {"root": query, "children": []}

    for cid, sim in hits:
        kw_root = meta[str(cid)]["keywords"][0]
        cluster_node = build_tree(kw_root, cid, depth=1) 
        cluster_node["sim"] = round(sim, 4)
        root["children"].append(cluster_node)
    return {"results": root }

# 로컬 실행용
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004)

    # uvicorn runtime.api:app --reload --port 8004