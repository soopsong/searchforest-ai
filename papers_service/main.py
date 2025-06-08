# papers_service/main.py
import random

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import json
import os

app = FastAPI(title="Papers Service (Stub)")


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

    citations: Optional[List[Citation]] = []
    references: Optional[List[Reference]] = []

    sim_score: float


# --- 응답 모델 ---
class PapersResponse(BaseModel):
    total_results: int
    max_display: int
    page: int
    page_size: int
    papers: List[Paper]


# BASE_DIR = os.path.dirname(__file__)
#
# # 1) 전역 로딩
# with open(os.path.join(BASE_DIR, "../data/inductive/test_checkpoint_collected.json"), "r", encoding="utf-8") as f:
#     paper_db = json.load(f)
#
# # 예시: 이미 생성한 키워드 → 논문 ID 매핑
# with open(os.path.join(BASE_DIR, "../data/inductive/result/kw2pids.json"), "r", encoding="utf-8") as f:
#     kw2pids = json.load(f)

# 1) 전역 로딩
with open("test_checkpoint_collected.json", "r", encoding="utf-8") as f:
    paper_db = json.load(f)

# 예시: 이미 생성한 키워드 → 논문 ID 매핑
with open("kw2pids.json", "r", encoding="utf-8") as f:
    kw2pids = json.load(f)


@app.get("/papers", response_model=PapersResponse)
def get_papers_by_keyword(
        kw: str = Query(..., description="검색할 키워드"),
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100)
):
    if kw not in kw2pids:
        print(f"Keyword '{kw}' not found.")
        all_pids = [
            "40108038",
            "59572248",
            "5799960",
            "14188576",
            "119242784"
        ]
        # raise HTTPException(status_code=404, detail=f"Keyword '{kw}' not found.")
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
            citations=[
                Citation(**c) for c in entry.get("citations", [])
                if c.get("paperId") is not None
            ],
            references=[
                Reference(**r) for r in entry.get("references", [])
                if r.get("paperId") is not None
            ],
            sim_score=random.uniform(0, 1)  # Stub score
        ))

    return PapersResponse(
        total_results=total,
        max_display=len(sliced),
        page=page,
        page_size=page_size,
        papers=papers
    )
