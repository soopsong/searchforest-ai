#!/usr/bin/env python3
# embed_keywords.py

import os
import argparse
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def main(keywords_path: str, index_path: str, id_map_path: str, model_name: str):
    # 1) 키워드 로드
    with open(keywords_path, "r", encoding="utf-8") as f:
        keywords = [line.split("\t")[0] for line in f if line.strip()]
    print(f"[1] Loaded {len(keywords)} keywords from {keywords_path!r}")

    # 2) 임베딩 계산
    print("[2] Loading SentenceTransformer and encoding keywords...")
    model = SentenceTransformer(model_name)
    embeddings = model.encode(keywords, convert_to_numpy=True).astype('float32')

    faiss.normalize_L2(embeddings)

    # 3) FAISS 인덱스 생성 (Inner Product → 코사인 유사도로 사용)
    dim = embeddings.shape[1]
    print(f"[3] Building FAISS index (dim={dim})...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # 4) 인덱스 및 ID 맵 저장
    print(f"[4] Saving index to {index_path!r} and id map to {id_map_path!r}...")
    faiss.write_index(index, index_path)
    with open(id_map_path, "w", encoding="utf-8") as f:
        for kw in keywords:
            f.write(kw + "\n")

    print("[✓] Done.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Encode keywords and build FAISS index"
    )
    p.add_argument(
        "--keywords",
        required=True,
        help="Path to keywords.txt"
    )
    p.add_argument(
        "--index",
        default="keyword.index",
        help="Output FAISS index file"
    )
    p.add_argument(
        "--id_map",
        default="keyword_ids.txt",
        help="Output keyword ID map (one keyword per line)"
    )
    p.add_argument(
        "--model",
        default="moka-ai/m3e-base",
        help="m3e model"
    )
    args = p.parse_args()

    main(
        keywords_path=args.keywords,
        index_path=args.index,
        id_map_path=args.id_map,
        model_name=args.model
    )
