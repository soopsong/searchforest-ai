import os
import json, hashlib
from typing import List, Dict, Optional, Tuple, Union
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import aioredis
import requests
from tree_mapping import extract_tree_mapping

# ────────────────────────────────────────────────────────────────
app = FastAPI(title="Graph Service with AI Inference")

# Redis 초기화용 글로벌
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")
redis: Optional[aioredis.Redis] = None

# 요청 모델
class GraphRequest(BaseModel):
    root: str
    top1: int = 5
    top2: int = 3

# 응답 트리 노드 구조
class KeywordNode(BaseModel):
    id: str
    value: float
    children: List["KeywordNode"]
KeywordNode.update_forward_refs()

# 전체 응답 구조
class GraphResponse(BaseModel):
    keyword_tree: KeywordNode
    
# Redis 연결
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
        print(f"✅ Connected to Redis at {REDIS_URL}")
    except Exception as e:
        print(f"⚠️ Redis 연결 실패, 캐시 미사용: {e}")
        redis = None

@app.on_event("shutdown")
async def shutdown_event():
    await redis.close()

# 캐시 키 생성 함수
def make_cache_key( root: str, top1: int, top2: int) -> str:
    # 파라미터 조합으로 고유 키 생성
    key_str = f"{root}|{top1}|{top2}"
    return "graph:" + hashlib.sha256(key_str.encode()).hexdigest()


# AI 서버 호출 함수
def fetch_keywords(query: str) -> list[str]:
    try:
        response = requests.get(
            "https://2f7a-165-194-104-91.ngrok-free.app/inference"
            params={"query": query, "top_k": 5}
        )
        response.raise_for_status()
        data = response.json()
        keywords = [child["kw"] for child in data["results"]["children"]]
        return keywords
    except Exception as e:
        print(f"[ERROR] AI 서버 호출 실패: {e}")
        return []

# AI 서버 호출 + 결과 캐싱
async def fetch_from_ai_and_cache(root: str, top1: int, top2: int):
    try:
        #response = requests.get("http://searchforest-ai:8004/inference", params={"query": root, "top_k": top1})
        response = requests.get("https://2f7a-165-194-104-91.ngrok-free.app/inference", params={"query": root, "top_k": top1})

        # response = requests.get("http://localhost:8004/inference", params={"query": root, "top_k": top1})

        response.raise_for_status()
        data = response.json()

        tree_data = data["results"]["children"]

        # 👉 트리 포맷 맞춰 변환
        mapping = {}
        for node in tree_data:
            lvl1_kw = node["id"]
            mapping[lvl1_kw] = {
                "value": node.get("sim", 0.8),
                "children": node.get("children", [])
            }

        keyword_tree = manual_tree_with_full_values(root, mapping)

        # pids 추출
        kw2pids = {}
        for node in tree_data:
            for child in node["children"]:
                kw2pids[child["id"]] = child["pids"]

        cache_key = make_cache_key(root, top1, top2)
        if redis:
            await redis.set(cache_key, json.dumps({"tree": keyword_tree, "kw2pids": kw2pids}), ex=3600)

        return keyword_tree, kw2pids

    except Exception as e:
        print(f"[ERROR] AI 호출 실패: {e}")
        raise

# /graph 엔드포인트
@app.post("/graph", response_model=GraphResponse)
async def build_graph(req: GraphRequest):

    cache_key = make_cache_key(req.root, req.top1, req.top2)
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            obj = json.loads(cached)
            return {"keyword_tree": obj["tree"], "kw2pids": obj["kw2pids"]}

    tree = await fetch_from_ai_and_cache(req.root, req.top1, req.top2)
    
    root, mapping = extract_tree_mapping(original_json)
    tree = manual_tree_with_full_values(root, mapping)
    tree_parsed = manual_tree_with_full_values(tree)

    return {"keyword_tree": tree_parsed, "kw2pids": kw2pids}


# /kw2pids 엔드포인트 (핑퐁용)
@app.get("/kw2pids")
async def get_kw2pids(query: str = Query(...), top1: int = 5, top2: int = 3):
    cache_key = make_cache_key(query, top1, top2)
    if redis:
        cached = await redis.get(cache_key)
        if cached:
            obj = json.loads(cached)
            return obj["kw2pids"]
    return {"message": "No cached kw2pids available."}
