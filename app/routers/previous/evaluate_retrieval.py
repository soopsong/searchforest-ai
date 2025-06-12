#!/usr/bin/env python3
# evaluate_retrieval.py

import json
import argparse

def precision_at_k(preds, golds, k):
    """Top-k 중 golds에 속하는 항목 비율"""
    if k == 0: return 0.0
    return sum(1 for p in preds[:k] if p in golds) / k

def recall_at_k(preds, golds, k):
    """golds 중 Top-k에 포함된 항목 비율"""
    if not golds: return 0.0
    return sum(1 for p in preds[:k] if p in golds) / len(golds)

def reciprocal_rank(preds, golds):
    """첫 번째 정답이 나오는 순위의 역수"""
    for i, p in enumerate(preds, start=1):
        if p in golds:
            return 1.0 / i
    return 0.0

def main(ground_truth_path, results_path, ks):
    # JSON 로드
    with open(ground_truth_path, 'r', encoding='utf-8') as f:
        ground_truth = json.load(f)
    with open(results_path, 'r', encoding='utf-8') as f:
        results = json.load(f)

    # 메트릭 초기화
    metrics = {f"P@{k}": [] for k in ks}
    metrics.update({f"R@{k}": [] for k in ks})
    metrics["MRR"] = []

    # 쿼리별 평가
    for query, golds in ground_truth.items():
        preds = results.get(query, [])
        for k in ks:
            metrics[f"P@{k}"].append(precision_at_k(preds, golds, k))
            metrics[f"R@{k}"].append(recall_at_k(preds, golds, k))
        metrics["MRR"].append(reciprocal_rank(preds, golds))

    # 평균 계산 및 출력
    print("=== Retrieval Evaluation ===")
    n = len(ground_truth)
    for name, vals in metrics.items():
        mean_val = sum(vals) / n if n > 0 else 0.0
        print(f"{name:6s}: {mean_val:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Evaluate retrieval performance with P@K, R@K, and MRR"
    )
    parser.add_argument(
        "--ground_truth", required=True,
        help="Path to ground_truth.json"
    )
    parser.add_argument(
        "--results", required=True,
        help="Path to results.json"
    )
    parser.add_argument(
        "--ks", nargs="+", type=int, default=[5, 10],
        help="Values of K for P@K and R@K"
    )
    args = parser.parse_args()

    main(args.ground_truth, args.results, args.ks)
