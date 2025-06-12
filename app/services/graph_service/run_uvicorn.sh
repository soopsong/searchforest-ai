#!/bin/bash

# 기본 실행 스크립트 for FastAPI with Uvicorn
# 실행: ./run_uvicorn.sh

echo "Starting FastAPI server..."
# uvicorn main:app --reload

# 현재 위치: ~/searchforest-ai/app/services/graph_service
PYTHONPATH=../../ uvicorn graph_service:app --reload --port 8002