import os
import json, hashlib
from typing import List, Dict, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import aioredis
from fastapi_utils.tasks import repeat_every
from data_util.logging import logger

from data_util.config import Config
from routers.graph_loader import GraphLoader
from routers.graph_builder import GraphBuilder
from routers.searcher import VectorKeywordSearcher

app = FastAPI(title="2-Depth 키워드 그래프 서비스")

# --- 요청 모델 ---
class GraphRequest(BaseModel):
    root_pid: Optional[str] = None   # 논문 ID를 직접 받거나
    root_kw: Optional[str] = None    # 또는 키워드를 받아도 됩니다
    top1: int = 5
    top2: int = 3

# --- 응답 모델 ---
class GraphResponse(BaseModel):
    graph: Dict
    kw2pids: Dict[str, List[str]]

# 1) Config 선언 및 paths 설정
cfg = Config()
cfg.train_path = "data/extracted/inductive"
cfg.train_file = "train.jsonl"
cfg.test_file  = "test.jsonl"
cfg.setting    = "inductive"
cfg.mode       = "test"
cfg.load_vocab = True
cfg.vocab_path = os.path.join(cfg.train_path, "vocab")

# 2) GraphLoader, GraphBuilder 초기화
loader = GraphLoader(cfg)
paths = {
    "train": os.path.join(cfg.train_path, cfg.train_file),
    "test":  os.path.join(cfg.train_path, cfg.test_file),
}
graph_dict, paper_meta = loader.load_graph_and_meta(paths)
builder = GraphBuilder()

# 3) 검색기 초기화
searcher = VectorKeywordSearcher(
    hf_model_name="moka-ai/m3e-base",
    index_path="indices/paper_ivf.index",
    id_map_path="indices/paper_ids.txt"
)

# 2) Redis 클라이언트 초기화 (앱 스타트업 시)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis: Optional[aioredis.Redis] = None

@app.on_event("startup")
async def startup_event():
    global redis
    # modern aioredis uses from_url
    try:
        redis = await aioredis.from_url(
            REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
            max_connections=10
        )
        logger.info(f"✅ Connected to Redis at {REDIS_URL}")
    except Exception as e:
        logger.warning(f"⚠️ Redis 연결 실패, 캐시 미사용: {e}")
        redis = None

@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()

def make_cache_key(root_pid: str, root_kw: str, top1: int, top2: int) -> str:
    # 파라미터 조합으로 고유 키 생성
    key_str = f"{root_pid}|{root_kw}|{top1}|{top2}"
    return "graph:" + hashlib.sha256(key_str.encode()).hexdigest()

# --- 엔드포인트: dummy_data 사용 ---
@app.post("/graph", response_model=GraphResponse)
async def build_graph(req: GraphRequest):

    # 1) 루트 논문 ID 결정 (req.root_pid or 키워드 검색)
    root_pid = req.root_pid
    if not root_pid:
        if not req.root_kw:
            raise HTTPException(400, "root_pid or root_kw required")
        candidates = searcher.search(req.root_kw, topk=1)
        if not candidates:
            raise HTTPException(404, "No paper found for keyword")
        root_pid = candidates[0]

    # 2) 캐시 키 생성 (root_pid가 정의된 후)
    cache_key = make_cache_key(root_pid, req.root_kw or root_pid, req.top1, req.top2)

    # 3) 캐시 확인
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    # 4) 그래프 생성
    builder.k1 = req.top1
    builder.k2 = req.top2
    graph_json, kw2pids = builder.build(
        root_kw   = req.root_kw or root_pid,
        root_pids = [root_pid],
        graph_dict=graph_dict,
        paper_meta=paper_meta
    )
    payload = {"graph": graph_json, "kw2pids": kw2pids}

    # 4) 캐시에 저장 (TTL 1시간)
    await redis.set(cache_key, json.dumps(payload, ensure_ascii=False), ex=3600)


    return payload


    # # 1) 루트 논문 ID 유효성 검사
    # if root_pid not in graph_dict:
    #     raise HTTPException(status_code=404, detail="Root paper_id not found")

    # # 2) k1, k2 업데이트
    # builder.k1 = req.top1
    # builder.k2 = req.top2

    # # 3) 2-Depth 그래프 생성
    # graph_json, kw2pids = builder.build(
    #     root_kw     = req.root_kw or root_pid,
    #     root_pids   = [root_pid],
    #     graph_dict  = graph_dict,
    #     paper_meta  = paper_meta
    # )

    # # 4) 반환
    # return {"graph": graph_json, "kw2pids": kw2pids}

    # # if req.root in IMPORTANT_TREES:
    # #     tree = IMPORTANT_TREES[req.root]
    # # else:
    # #     tree = get_dummy_tree_with_context(req.root, req.top1, req.top2)
    # # return {"keyword_tree": tree}