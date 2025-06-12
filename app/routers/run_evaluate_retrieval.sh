#!/usr/bin/env bash
set -e

# 1) Inductive 평가
echo "=== Inductive Evaluation ==="
python evaluate_retrieval.py \
  --index inductive/paper.index \
  --id_map inductive/paper_ids.txt \
  --test_meta inductive/test.jsonl \
  --topk 5 \
  > inductive_metrics.txt

# 2) Transductive 평가
echo "=== Transductive Evaluation ==="
python evaluate_retrieval.py \
  --index transductive/paper.index \
  --id_map transductive/paper_ids.txt \
  --test_meta transductive/test/papers.jsonl \
  --topk 5 \
  > transductive_metrics.txt

# 3) 결과 요약
echo -e "\n--- Summary ---"
echo "Inductive metrics:"
cat inductive_metrics.txt
echo "Transductive metrics:"
cat transductive_metrics.txt
