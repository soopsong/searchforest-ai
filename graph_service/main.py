from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

# ① dummy_data 모듈에서 get_dummy_tree 함수 import
from dummy_data import get_dummy_tree

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
    children: List["KeywordNode"]
KeywordNode.update_forward_refs()

# --- 응답 모델 ---
class GraphResponse(BaseModel):
    keyword_tree: KeywordNode

# --- 엔드포인트: dummy_data 사용 ---
@app.post("/graph", response_model=GraphResponse)
def build_graph(req: GraphRequest):
    # get_dummy_tree로 더미 트리 생성
    tree = get_dummy_tree(req.root, top1=req.top1, top2=req.top2)
    return {"keyword_tree": tree}
