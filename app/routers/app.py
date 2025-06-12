from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
# 전역 인스턴스: searcher, loader, extractor, builder

@app.get('/graph')
def get_graph(kw: str):
    graph_json = builder.build_graph_for_kw(kw)
    return graph_json

@app.get('/papers')
def get_papers(kw: str):
    pids = builder.kw2pids.get(kw)
    if not pids:
        raise HTTPException(status_code=404, detail="Keyword not found")
    return [paper_meta[pid] for pid in pids]