#!/usr/bin/env bash

# -----------------------------
# start_server.sh
# -----------------------------

# # 1) Conda 환경 활성화
# echo "[1/3] Activating Conda environment 'cgsum'..."
# # 필요에 따라 conda.sh 경로를 조정하세요
# source ~/miniconda3/etc/profile.d/conda.sh
# conda activate cgsum

# 2) 작업 디렉토리 이동
echo "[2/3] Changing working directory to project root..."
cd "$(dirname "$0")"/..   # 스크립트 위치 기준으로 한 단계 위로

# 3) Uvicorn 서버 실행
echo "[3/3] Starting Uvicorn server..."
exec uvicorn services.graph_service.main:app \
     --reload \
     --host 0.0.0.0 \
     --port 8000
