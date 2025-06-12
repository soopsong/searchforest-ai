# papers_service/main.py
import random

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI(title="Papers Service")


class Author(BaseModel):
    name: str


class Citation(BaseModel):
    paperId: str
    title: Optional[str]
    year: Optional[int]


class Reference(BaseModel):
    paperId: str
    title: Optional[str]
    year: Optional[int]


# --- 논문 객체 정의 ---
class Paper(BaseModel):
    paper_id: str
    abstract: Optional[str]
    title: Optional[str]

    url: Optional[str]
    venue: Optional[str]
    year: Optional[int]

    reference_count: Optional[int]
    citation_count: Optional[int]
    influentialCitationCount: Optional[int]

    fieldsOfStudy: Optional[List[str]]
    tldr: Optional[str]
    authors: List[Author]

    sim_score: float


# --- 응답 모델 ---
class PapersResponse(BaseModel):
    total_results: int
    max_display: int
    page: int
    page_size: int
    papers: List[Paper]



def make_cache_key(root, top1, top2):
    key_str = f"{root}|{top1}|{top2}"
    return "keyword_tree:graph:" + hashlib.sha256(key_str.encode()).hexdigest()


def fetch_keyword_tree_from_graph_service(query: str) -> dict:
    response = requests.get("http://graph-service:8002/keyword_tree", params={"query": query})
    return response.json()

@app.get("/papers", response_model=PapersResponse)
def get_papers_by_keyword(
        kw: str = Query(..., description="클릭한 키워드"),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
):

    response = requests.post("http://graph-service:8002/graph", json={
        "root": kw,
        "top1": 10,
        "top2": 3
    })


    keyword_tree = response.json().get("keyword_tree")

    response = requests.get("http://graph-service:8002/keyword_tree", params={"query": "AI"})
    kw2pids = response.json()



    keyword_tree_json = redis.get(f"keyword_tree:{cache_key}")
    keyword_tree = json.loads(keyword_tree_json)

    key = make_cache_key("pid123", "AI", 5, 3)
    cached = redis.get(key)
    if cached:
        kw2pids = json.loads(cached)


    if kw not in kw2pids:
        raise HTTPException(status_code=404, detail=f"Keyword '{kw}' not found.")
    else:
        all_pids = kw2pids[kw]

    # 페이징
    total = len(all_pids)
    start = (page - 1) * page_size
    end = min(start + page_size, total)
    sliced = all_pids[start:end]

    papers = []
    for pid in sliced:
        if pid not in paper_db:
            continue
        entry = paper_db[pid]
        papers.append(Paper(
            paper_id=pid,
            title=entry.get("title"),
            abstract=entry.get("abstract"),
            url=entry.get("url"),
            venue=entry.get("venue"),
            year=entry.get("year"),
            reference_count=entry.get("referenceCount"),
            citation_count=entry.get("citationCount"),
            influentialCitationCount=entry.get("influentialCitationCount"),
            fieldsOfStudy=entry.get("fieldsOfStudy"),
            tldr=entry.get("tldr", {}).get("text") if entry.get("tldr") else None,
            authors=[Author(name=a["name"]) for a in entry.get("authors", [])],
            sim_score=random.uniform(0, 1)  # Stub score
        ))

    return PapersResponse(
        total_results=total,
        max_display=len(sliced),
        page=page,
        page_size=page_size,
        papers=papers
    )

@app.get("/keyword_tree")
async def get_keyword_tree(query: str = Query(...)):
    cache_key = f"kw2pids:{query}"
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            return json.loads(cached)
    return {"message": "No cached keyword->pids mapping found."}
