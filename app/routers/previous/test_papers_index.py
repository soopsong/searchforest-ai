#!/usr/bin/env python3
# test_papers_index.py

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ——————————————————————————————————————————————————————————
# 설정
INDEX_PATH  = "paper.index"
ID_MAP_PATH = "paper_ids.txt"
MODEL_NAME = "moka-ai/m3e-base"
# ——————————————————————————————————————————————————————————

def main():
    # 1) FAISS 인덱스 & ID 맵 로드
    index = faiss.read_index(INDEX_PATH)
    print(f"[1] Loaded FAISS index with {index.ntotal} vectors.")
    with open(ID_MAP_PATH, "r", encoding="utf-8") as f:
        paper_ids = [line.strip() for line in f if line.strip()]
    print(f"[2] Loaded {len(paper_ids)} paper IDs.")

    # 2) 쿼리 임베딩 + L2 정규화 (Cosine)
    model = SentenceTransformer(MODEL_NAME)
    query = "quantum variational algorithms"  # 테스트할 쿼리
    qv = model.encode(query, convert_to_numpy=True).astype('float32')
    # reshape 후 정규화
    qv = qv.reshape(1, -1)
    faiss.normalize_L2(qv)

    # 3) 검색
    k = 5
    D, I = index.search(qv, k)

    # 4) 출력
    print(f"\nTop {k} papers for query: {query!r}")
    for score, idx in zip(D[0], I[0]):
        pid = paper_ids[idx] if idx < len(paper_ids) else "UNKNOWN"
        print(f"  {pid:<20}  sim={score:.4f}")

if __name__ == "__main__":
    main()
