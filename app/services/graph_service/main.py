import os
import json
from typing import List, Dict
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from data_util.config import Config
from routers.graph_loader import GraphLoader
from routers.graph_builder import GraphBuilder

app = FastAPI(title="2-Depth 키워드 그래프 서비스")

# --- 요청 모델 ---
class GraphRequest(BaseModel):
    root_pid: str       # 논문 ID를 직접 받거나
    root_kw: str        # 또는 키워드를 받아도 됩니다
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

# --- 엔드포인트: dummy_data 사용 ---
@app.post("/graph", response_model=GraphResponse)
def build_graph(req: GraphRequest):
    # 1) 루트 논문 ID 유효성 검사
    if req.root_pid not in graph_dict:
        raise HTTPException(status_code=404, detail="Root paper_id not found")

    # 2) k1, k2 업데이트
    builder.k1 = req.top1
    builder.k2 = req.top2

    # 3) 2-Depth 그래프 생성
    graph_json, kw2pids = builder.build(
        root_kw     = req.root_kw or req.root_pid,
        root_pids   = [req.root_pid],
        graph_dict  = graph_dict,
        paper_meta  = paper_meta
    )

    # 4) 반환
    return {"graph": graph_json, "kw2pids": kw2pids}

    # if req.root in IMPORTANT_TREES:
    #     tree = IMPORTANT_TREES[req.root]
    # else:
    #     tree = get_dummy_tree_with_context(req.root, req.top1, req.top2)
    # return {"keyword_tree": tree}