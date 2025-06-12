#!/usr/bin/env python3
# searcher.py

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class VectorKeywordSearcher:
    """
    HuggingFace + FAISS 기반 키워드 검색기
    """
    def __init__(
        self,
        hf_model_name: str,
        index_path: str,
        id_map_path: str
    ):
        # 1) HuggingFace SentenceTransformer 로드
        self.model = SentenceTransformer(hf_model_name)
        # 2) FAISS 인덱스 로드 (내부는 Inner Product)
        self.index = faiss.read_index(index_path)
        # 3) 키워드 ID 맵 로드
        with open(id_map_path, 'r', encoding='utf-8') as f:
            self.id_map = [line.strip() for line in f]

    def search(self, query: str, top_k: int = 10) -> List[Tuple[str, float]]:
        """
        텍스트(query)를 임베딩하여 키워드 인덱스에서 유사 키워드(top_k)를 반환
        :param query: 검색할 텍스트 (abstract 등)
        :param top_k: 상위 추출할 키워드 개수
        :return: [(keyword, similarity), ...]
        """
        # 1) Query 임베딩
        qv = self.model.encode(query, convert_to_numpy=True).astype('float32')
        # 2) L2 정규화하여 Inner Product를 cosine 유사도로 사용
        faiss.normalize_L2(qv.reshape(1, -1))
        # 3) FAISS 검색
        D, I = self.index.search(qv.reshape(1, -1), top_k)
        results: List[Tuple[str, float]] = []
        for dist, idx in zip(D[0], I[0]):
            if idx < len(self.id_map):
                kw = self.id_map[idx]
                sim = float(dist)
                results.append((kw, sim))
        return results


if __name__ == "__main__":
    # 예시 사용법
    searcher = VectorKeywordSearcher(
        hf_model_name="moka-ai/m3e-base",
        index_path="keyword.index",
        id_map_path="keyword_ids.txt"
    )
    query = "quantum computation"
    for kw, score in searcher.search(query, top_k=5):
        print(f"{kw}: {score:.4f}")

