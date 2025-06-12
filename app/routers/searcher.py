
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple

class VectorKeywordSearcher:
    """
    HuggingFace M3E + FAISS 기반 키워드 → 논문 ID 검색기
    """
    def __init__(self,
                 hf_model_name: str,
                 index_path: str,
                 id_map_path: str):
        # 1) HuggingFace SentenceTransformer 로드
        self.model = SentenceTransformer(hf_model_name)
        # 2) FAISS 인덱스 로드
        self.index = faiss.read_index(index_path)
        # 3) 논문 ID 매핑 (벡터 인덱스 순서 → paper_id)
        with open(id_map_path, 'r') as f:
            self.id_map = [line.strip() for line in f]

    def search(self, query: str, topk: int = 10) -> List[Tuple[str, float]]:
            # 1) Query 임베딩
            qv = self.model.encode(query, convert_to_numpy=True).astype('float32')
            # 2) FAISS 검색
            D, I = self.index.search(np.array([qv]), topk)
            distances = D[0]
            idxs      = I[0]
            results: List[Tuple[str,float]] = []
            for dist, idx in zip(distances, idxs):
                if idx < len(self.id_map):
                    pid = self.id_map[idx]
                    sim = float(1.0 / (1.0 + dist))  # 거리→유사도로 변환
                    results.append((pid, sim))
            return results



if __name__ == "__main__":
    searcher = VectorKeywordSearcher(
        hf_model_name="moka-ai/m3e-base",
        index_path="indices/paper_ivf.index",
        id_map_path="indices/paper_ids.txt"
    )
    print(searcher.search("quantum linear systems", topk=3))