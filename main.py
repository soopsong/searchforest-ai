from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# 1) Pydantic 모델 정의

class KeywordNode(BaseModel):
    id: str
    value: float
    children: List["KeywordNode"]
KeywordNode.update_forward_refs()

class GraphResponse(BaseModel):
    keyword_tree: KeywordNode

class Paper(BaseModel):
    paper_id: str
    title: str
    abstract: str
    authors: List[str]
    year: int
    citation_count: Optional[int]
    sim_score: float
    summary: Optional[str] = None

class PapersResponse(BaseModel):
    total_results: int
    max_display:   int
    page:          int
    page_size:     int
    papers:        List[Paper]

class SearchResponse(PapersResponse, GraphResponse):
    pass


# 2) 라우터 시그니처만 구현 (로직은 TODO)

@app.get("/api/graph", response_model=GraphResponse)
def api_graph(
    root: str = Query(...),
    top1: int = Query(5, ge=1, le=20),
    top2: int = Query(3, ge=1, le=20)
):
    """
    TODO: build_keyword_tree 호출해서 radial-tree 형태로 반환
    """
    raise NotImplementedError


@app.get("/api/papers", response_model=PapersResponse)
def api_papers(
    query: str = Query(...),
    sort_by: str = Query("similarity"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    include_summary: bool = Query(False)
):
    """
    TODO: search_papers + paginate + summary 옵션 적용
    """
    raise NotImplementedError


@app.get("/api/search", response_model=SearchResponse)
def api_search(
    root: str = Query(...),
    sort_by: str = Query("similarity"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    include_summary: bool = Query(False)
):
    """
    TODO: api_graph + api_papers 조합해서 한번에 반환
    """
    raise NotImplementedError