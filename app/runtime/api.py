# runtime/api.py
from fastapi import FastAPI, Query
from pydantic import BaseModel
import uvicorn, json

from cluster_searcher import search_clusters, cluster2pids, meta
from graph_builder    import build_tree

app = FastAPI(title="SearchForest-AI Recommend API")

class RecResult(BaseModel):
    cluster: int
    sim:     float
    tree:    dict

class RecResponse(BaseModel):
    query: str
    results: list[RecResult]


@app.get("/recommend", response_model=RecResponse)
def recommend(
        query: str = Query(..., description="자유 입력 쿼리"),
        top_k: int = Query(3, gt=0, le=10)):
    hits = search_clusters(query, top_k)
    results = []
    for cid, sim in hits:
        pids = cluster2pids.get(cid, [])
        root_kw = meta[str(cid)]["keywords"][0] if meta[str(cid)]["keywords"] else query
        tree = build_tree(root_kw, pids, cluster2pids)
        results.append({"cluster": cid, "sim": sim, "tree": tree})
    return {"query": query, "results": results}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
