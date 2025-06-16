# papers_service/main.py 

import os, json, random, asyncio
from typing import List, Dict, Optional

from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
import httpx

app = FastAPI(title="Papers Service")

# ───────── Pydantic Models ─────────
class Author(BaseModel):
    name: str

class Paper(BaseModel):
    paper_id: str
    title:      Optional[str]
    abstract:   Optional[str]
    url:        Optional[str]
    venue:      Optional[str]
    year:       Optional[int]
    reference_count:          Optional[int]
    citation_count:           Optional[int]
    influentialCitationCount: Optional[int]
    fieldsOfStudy:            Optional[List[str]]
    tldr:       Optional[str]
    authors:    List[Author]
    sim_score:  float

class PapersResponse(BaseModel):
    total_results: int
    max_display:   int
    page:          int
    page_size:     int
    papers:        List[Paper]

# ───────── Data Load ─────────
BASE_DIR = os.path.join(os.path.dirname(__file__), "data")

def safe_load(fname: str) -> dict:
    path = os.path.join(BASE_DIR, fname)
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️  {fname} not found → 빈 dict 사용")
        return {}

paper_db: Dict[str, dict]        = safe_load("paper_db.json")
kw2pids:   Dict[str, List[str]]  = safe_load("kw2pids.json")
save_lock  = asyncio.Lock()                      # 파일 캐시 동시 접근 보호

# ────────────── Helper ──────────────
def build_paper(pid: str) -> Paper:
    e = paper_db[pid]
    return Paper(
        paper_id              = pid,
        title                 = e.get("title"),
        abstract              = e.get("abstract"),
        url                   = e.get("url"),
        venue                 = e.get("venue"),
        year                  = e.get("year"),
        reference_count       = e.get("referenceCount"),
        citation_count        = e.get("citationCount"),
        influentialCitationCount = e.get("influentialCitationCount"),
        fieldsOfStudy         = e.get("fieldsOfStudy"),
        tldr                  = (e.get("tldr") or {}).get("text"),  # ← 수정
        authors               = [Author(name=a["name"])
                                 for a in e.get("authors", [])],
        sim_score             = random.uniform(0, 1),   # stub
    )

def paginate(ids: List[str], page: int, page_size: int):
    total = len(ids)
    start = (page - 1) * page_size
    return ids[start:start + page_size], total

async def build_papers(ids: List[str]) -> List[Paper]:
    papers: List[Paper] = []
    for pid in ids:
        if await ensure_paper(pid):
            papers.append(build_paper(pid))
    return papers

# ───────── API ─────────
@app.get("/papers", response_model=PapersResponse)
async def get_papers(
    root: str = Query(..., description="검색 루트(처음 입력)"),
    kw:   str = Query(..., description="사용자가 선택한 키워드"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    ids = await ensure_kw2pids(root, kw)
    if not ids:
        raise HTTPException(404, f"Keyword '{kw}' not found")

    sliced, total = paginate(ids, page, page_size)

    # paper_db 에 존재하는 PID 만 반환
    papers = [build_paper(pid) for pid in sliced if pid in paper_db]

    return PapersResponse(
        total_results = total,
        max_display   = len(papers),
        page          = page,
        page_size     = page_size,
        papers        = papers,
    )

GRAPH_BASE = os.getenv("GRAPH_URL", "http://graph-service:8002")

async def ensure_kw2pids(root: str, keyword: str,
                         top1: int = 5, top2: int = 3) -> List[str]:
    """keyword 가 캐시에 없으면 graph-service 를 호출해 kw2pids 갱신"""
    if keyword in kw2pids:
        return kw2pids[keyword]

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{GRAPH_BASE}/graph",
            json={"root": keyword, "top1": top1, "top2": top2},
            timeout=15
        )
    if resp.status_code != 200:
        raise HTTPException(502, "graph_service error")

    data = resp.json()
    kw2pids.update(data["kw2pids"])

    # 🔽 파일 캐시 저장 시도 → 읽기 전용이면 무시
    try:
        async with save_lock:
            path = os.path.join(BASE_DIR, "kw2pids.json")
            with open(path, "w") as f:
                json.dump(kw2pids, f, ensure_ascii=False)
    except OSError:
        # read-only · 컨테이너 환경에선 무시하고 넘어감
        pass

    return kw2pids.get(keyword, [])
    