import os, json, hashlib
from typing import List, Dict, Optional
from fastapi import FastAPI, Query
from pydantic import BaseModel
import aioredis, requests
import httpx

from json_to_tree_and_kw2pid import manual_tree_with_full_values

# ─────────────────────────────
app = FastAPI(title="Graph Service with AI Inference")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
redis: Optional[aioredis.Redis] = None

# ───────── Models ────────────
class GraphRequest(BaseModel):
    root: str
    top1: int = 5
    top2: int = 3

class KeywordNode(BaseModel):
    id: str
    value: float
    children: List["KeywordNode"]
KeywordNode.update_forward_refs()

class GraphResponse(BaseModel):          # ✨
    keyword_tree: KeywordNode
    kw2pids: Dict[str, List[str]]

# ───────── Redis Events ──────
@app.on_event("startup")
async def startup_event():
    global redis
    try:
        redis = await aioredis.from_url(
            REDIS_URL, encoding="utf-8", decode_responses=True, max_connections=10
        )
        print(f"✅ Connected to Redis at {REDIS_URL}")
    except Exception as e:
        print(f"⚠️ Redis 연결 실패, 캐시 미사용: {e}")
        redis = None

@app.on_event("shutdown")
async def shutdown_event():
    if redis:                            # ✨
        await redis.close()

# ───────── Utils ────────────
def make_cache_key(root: str, top1: int, top2: int) -> str:
    return "graph:" + hashlib.sha256(f"{root}|{top1}|{top2}".encode()).hexdigest()

async def fetch_from_ai_and_cache(root: str, top1: int, top2: int):
    url = "https://58b9-165-194-104-91.ngrok-free.app/inference"
    params = {"query": root, "top_k": top1, "top2": top2}

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()

    # 2-1) keyword_tree
    mapping = { n["id"]:{"value": n.get("sim",0.8),"children": n.get("children",[])}
                for n in data["results"]["children"][:top1] }
    keyword_tree = manual_tree_with_full_values(root, mapping)

    # 2-2) kw2pids  ☑ root + 1-depth + 2-depth
    kw2pids = {}

    # root → 모든 1-depth pids 합집합
    root_pids = []
    for n in data["results"]["children"][:top1]:
        root_pids.extend(n.get("pids", []))
    kw2pids[root] = root_pids

    # 1-depth
    for n in data["results"]["children"][:top1]:
        if "pids" in n:
            kw2pids[n["id"]] = n["pids"]

        # 2-depth
        for child in n.get("children", []):
            if "pids" in child:
                kw2pids[child["id"]] = child["pids"]

    if redis:
        await redis.set(
            make_cache_key(root, top1, top2),
            json.dumps({"keyword_tree": keyword_tree, "kw2pids": kw2pids}),
            ex=3600,
        )
    return keyword_tree, kw2pids

# ───────── API ────────────
@app.post("/graph", response_model=GraphResponse)
async def build_graph(req: GraphRequest):
    cache_key = make_cache_key(req.root, req.top1, req.top2)
    if redis and (cached := await redis.get(cache_key)):
        obj = json.loads(cached)
        return obj                                  # FastAPI가 모델로 자동 직렬화

    keyword_tree, kw2pids = await fetch_from_ai_and_cache(
        req.root, req.top1, req.top2
    )

    
    return {"keyword_tree": keyword_tree, "kw2pids": kw2pids}   # ✨

@app.get("/kw2pids")
async def get_kw2pids(query: str = Query(...), top1: int = 5, top2: int = 3):
    if redis and (cached := await redis.get(make_cache_key(query, top1, top2))):
        return json.loads(cached)["kw2pids"]
    return {"message": "No cached kw2pids available."}