# graph_service/Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY graph_service.py .

COPY tree_mapping.py .


# FastAPI Uvicorn 실행
CMD ["uvicorn", "graph_service:app", "--host", "0.0.0.0", "--port", "8002"]