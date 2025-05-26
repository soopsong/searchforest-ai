# graph_service/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

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

# --- 엔드포인트 스텁 ---
@app.post("/graph", response_model=GraphResponse)
def build_graph(req: GraphRequest):
    # TODO: 실제 키워드 그래프 로직으로 교체
    # 여기서는 root 와 top1/top2 값을 반영한 더미 트리 생성
    children = []
    for label, val in [("A", 0.9), ("B", 0.85)][:req.top1]:
        grandchildren = [
            {"id": f"{req.root}-{label}-{i+1}", "value": val - 0.1*(i+1), "children": []}
            for i in range(req.top2)
        ]
        children.append({
            "id": f"{req.root}-{label}",
            "value": val,
            "children": grandchildren
        })
    tree = {
        "id": req.root,
        "value": 1.0,
        "children": children
    }
    return {"keyword_tree": tree}