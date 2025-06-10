from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

# ① dummy_data 모듈에서 get_dummy_tree 함수 import
from dummy_data import get_dummy_tree_with_context_and_example
from graph_service.conditional_dummy_tree import manual_tree_with_full_values, IMPORTANT_TREES

app = FastAPI(title="Graph Service (Stub)")

# --- 요청 모델 ---
class GraphRequest(BaseModel):
    root: str
    top1: int = 5
    top2: int = 3

# --- 키워드 노드 재귀 정의 ---
class KeywordNode(BaseModel):
    id: str
    value: float
    example: Optional[str]
    children: List["KeywordNode"]
KeywordNode.update_forward_refs()

# --- 응답 모델 ---
class GraphResponse(BaseModel):
    keyword_tree: KeywordNode

# --- 엔드포인트: dummy_data 사용 ---
@app.post("/graph", response_model=GraphResponse)
def build_graph(req: GraphRequest):
    if req.root in IMPORTANT_TREES:
        tree = IMPORTANT_TREES[req.root]
    else:
        tree = get_dummy_tree_with_context_and_example(req.root, req.top1, req.top2)
    return {"keyword_tree": tree}