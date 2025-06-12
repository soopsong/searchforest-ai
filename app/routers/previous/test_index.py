#!/usr/bin/env python3
# test_index.py

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1) 로드
INDEX_PATH = "keyword.index"
ID_MAP_PATH = "keyword_ids.txt"
MODEL_NAME = "moka-ai/m3e-base"

# FAISS 인덱스 읽기
index = faiss.read_index(INDEX_PATH)
print(f"Loaded FAISS index with {index.ntotal} vectors.")

# 키워드 ID 맵 읽기
with open(ID_MAP_PATH, "r", encoding="utf-8") as f:
    keywords = [line.strip() for line in f]
print(f"Loaded {len(keywords)} keywords in ID map.")

# 2) 쿼리 임베딩 & 검색
model = SentenceTransformer(MODEL_NAME)
query = "quantum computation"  # 원하는 테스트 쿼리
qv = model.encode(query, convert_to_numpy=True).astype('float32')
# 1×d 형태로 reshape 한 뒤 정규화
qv = qv.reshape(1, -1)
faiss.normalize_L2(qv)


# Inner-Product 기반 top-k 검색
k = 10
D, I = index.search(qv, k)

print(f"\nTop {k} keywords for query: {query!r}")
for score, idx in zip(D[0], I[0]):
    print(f"  {keywords[idx]:<30}  sim={score:.4f}")
