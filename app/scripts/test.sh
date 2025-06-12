#!/bin/bash

# 환경 활성화
echo "[STEP 1] Activating Conda Environment..."
# source /home/dswang/anaconda3/etc/profile.d/conda.sh  # 시스템에 맞게 경로 조정
# conda deactivate
# conda activate cgsum

# 실행 디렉토리로 이동 (필요시)
# cd /path/to/your/project

# 로그 디렉토리 생성
mkdir -p logs

# 테스트 실행
echo "[STEP 2] Running CGSum Test Script..."
python ../tests/test_CGSum.py \
  --visible_gpu 0 \
  --model_dir ../model/model_save \
  --model_name CGSum_inductive_1hopNbrs.pt \
  --setting inductive \
  --dataset_dir ../data/extracted/inductive \
  --decode_dir ../output/decode_path \
  --result_dir ../output/results \
  --min_dec_steps 130 \
  > logs/test_$(date +%Y%m%d_%H%M%S).log 2>&1

echo "[STEP 3] Done. Log saved in ./logs/"
