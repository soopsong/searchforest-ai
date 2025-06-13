# papers_service/main.py
import os, json, random
from typing import List, Optional, Dict

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Papers Service (Stub)")

# ────────────── Pydantic Models ──────────────
class Author(BaseModel):
    name: str

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

class PapersResponse(BaseModel):
    total_results: int
    max_display: int
    page: int
    page_size: int
    papers: List[Paper]

# ────────────── Data Load ──────────────
BASE_DIR = os.path.join(os.path.dirname(__file__), "data")
with open(os.path.join(BASE_DIR, "inductive_test_checkpoint_collected.json"), encoding="utf-8") as f:
    paper_db: Dict[str, dict] = json.load(f)

with open(os.path.join(BASE_DIR, "kw2pids.json"), encoding="utf-8") as f:
    kw2pids: Dict[str, List[str]] = json.load(f)

# ────────────── Helper ──────────────
def build_paper(pid: str) -> Paper:
    entry = paper_db[pid]
    return Paper(
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
        sim_score=random.uniform(0, 1),  # stub
    )

def paginate(ids: List[str], page: int, page_size: int):
    total = len(ids)
    max_page = max((total - 1) // page_size + 1, 1)
    if page > max_page:
        return [], total
    start = (page - 1) * page_size
    return ids[start : start + page_size], total

# ────────────── API ──────────────
@app.get("/papers", response_model=PapersResponse)
def get_random_papers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    sample_ids = random.sample(list(paper_db.keys()), k=min(40, len(paper_db)))
    sliced, total = paginate(sample_ids, page, page_size)
    return PapersResponse(
        total_results=total,
        max_display=len(sliced),
        page=page,
        page_size=page_size,
        papers=[build_paper(pid) for pid in sliced],
    )

@app.get("/papers/by_keyword", response_model=PapersResponse)  # ✨
def get_papers_by_keyword(
    kw: str = Query(..., description="검색 키워드"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    if kw not in kw2pids:
        raise HTTPException(status_code=404, detail=f"Keyword '{kw}' not found.")

    ids = kw2pids[kw]
    sliced, total = paginate(ids, page, page_size)
    papers = [build_paper(pid) for pid in sliced if pid in paper_db]

    return PapersResponse(
        total_results=total,
        max_display=len(papers),
        page=page,
        page_size=page_size,
        papers=papers,
    )
 