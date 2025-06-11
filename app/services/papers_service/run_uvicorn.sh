#!/bin/bash

# 기본 실행 스크립트 for FastAPI with Uvicorn
# 실행: ./run_uvicorn.sh

echo "Starting FastAPI server..."
uvicorn main:app --reload