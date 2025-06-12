#!/usr/bin/env python3
# extract_keywords.py

import os
import argparse
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

def main(tldr_dir: str, output_path: str, k: int, max_df: float, min_df: int, max_features: int):
    # 1) 모든 tldr 텍스트 읽어오기
    all_texts = []
    for fname in os.listdir(tldr_dir):
        if fname.endswith(".txt"):
            path = os.path.join(tldr_dir, fname)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read().strip()
                if text:
                    all_texts.append(text)
    print(f"[1] Loaded {len(all_texts)} summaries from {tldr_dir!r}")

    # 2) TF-IDF 벡터라이저 설정
    vec = TfidfVectorizer(
        stop_words='english',
        ngram_range=(1,2),
        max_df=max_df,
        min_df=min_df,
        max_features=max_features
    )

    # 3) fit & transform
    print("[2] Fitting TF-IDF vectorizer...")
    X = vec.fit_transform(all_texts)
    # scikit-learn 버전 호환: get_feature_names_out 없으면 get_feature_names 사용
    if hasattr(vec, "get_feature_names_out"):
        feature_names = vec.get_feature_names_out()
    else:
        feature_names = vec.get_feature_names()

    # 4) 전역 TF-IDF 총합 계산
    print("[3] Summing TF-IDF scores across corpus...")
    sums = np.asarray(X.sum(axis=0)).ravel()
    keyword_scores = list(zip(feature_names, sums))
    keyword_scores.sort(key=lambda x: x[1], reverse=True)

    # 5) 상위 K개 키워드 뽑아서 파일로 저장
    print(f"[4] Writing top {k} keywords to {output_path!r}...")
    with open(output_path, "w", encoding="utf-8") as fout:
        for kw, score in keyword_scores[:k]:
            fout.write(f"{kw}\t{score:.6f}\n")

    print("[✓] Done.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Extract global top-N TF-IDF keywords from a directory of tldr summaries"
    )
    p.add_argument(
        "--tldr_dir",
        required=True,
        help="Path to directory containing .txt summary files"
    )
    p.add_argument(
        "--output",
        default="keywords.txt",
        help="Path to write the keyword-score list"
    )
    p.add_argument(
        "--top_k",
        type=int,
        default=10000,
        help="Number of top keywords to save"
    )
    p.add_argument(
        "--max_df",
        type=float,
        default=0.8,
        help="Ignore terms that appear in > max_df fraction of documents"
    )
    p.add_argument(
        "--min_df",
        type=int,
        default=5,
        help="Ignore terms that appear in fewer than min_df documents"
    )
    p.add_argument(
        "--max_features",
        type=int,
        default=50000,
        help="Maximum size of the vocabulary"
    )
    args = p.parse_args()

    main(
        tldr_dir=args.tldr_dir,
        output_path=args.output,
        k=args.top_k,
        max_df=args.max_df,
        min_df=args.min_df,
        max_features=args.max_features
    )
