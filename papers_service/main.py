# papers_service/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from dummy_data import get_dummy_papers

app = FastAPI(title="Papers Service (Stub)")

# --- 요청 모델 ---
class PapersRequest(BaseModel):
    query: str
    sort_by: str      # "similarity" | "popularity" | "latest"
    page: int = 1
    page_size: int = 20
    include_summary: bool = False

# --- 논문 객체 정의 ---
class Paper(BaseModel):
    paper_id: str
    title: str
    abstract: str
    authors: List[str]
    year: int
    citation_count: Optional[int]
    sim_score: float
    summary: Optional[str] = None

# --- 응답 모델 ---
class PapersResponse(BaseModel):
    total_results: int
    max_display: int
    page: int
    page_size: int
    papers: List[Paper]

@app.post("/papers", response_model=PapersResponse)
def list_papers(req: PapersRequest):
    # ① 더미 데이터 로드
    all_papers = get_dummy_papers()
    total = len(all_papers)
    max_display = total

    # ② 페이징
    start = (req.page - 1) * req.page_size
    end = min(start + req.page_size, max_display)
    page_items = all_papers[start:end]

    # ③ include_summary 옵션 적용
    papers = []
    for rec in page_items:
        data = rec.copy()
        if not req.include_summary:
            data.pop("summary", None)
        papers.append(Paper(**data))

    return {
        "total_results": total,
        "max_display":   max_display,
        "page":          req.page,
        "page_size":     req.page_size,
        "papers":        papers
    }