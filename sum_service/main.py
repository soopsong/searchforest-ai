# sum_service/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from dummy_data import get_dummy_summary

app = FastAPI(title="Summarization Service (Stub)")

# 요청 모델
class SummRequest(BaseModel):
    paper_id: str

# 응답 모델
class SummResponse(BaseModel):
    paper_id: str
    summary: str

@app.post("/summarize", response_model=SummResponse)
def summarize(req: SummRequest):
    # 더미 데이터 함수 호출
    summary = get_dummy_summary(req.paper_id)
    return {"paper_id": req.paper_id, "summary": summary}