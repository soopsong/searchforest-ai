from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryInput(BaseModel):
    query: str

@app.post("/predict")
def predict(input: QueryInput):
    # 나중에 여기에 모델 붙이기
    return {
        "keywords": ["고양이", "강아지", "집사", "냥이"]
    }
