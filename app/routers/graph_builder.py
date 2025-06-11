# routers/graph_builder.py

import json
import numpy as np
from typing import Dict, List, Set, Tuple, Optional
from sentence_transformers import SentenceTransformer
from routers.keyword_extractor import TFIDFExtractor
from routers.searcher import VectorKeywordSearcher


class GraphBuilder:
    def __init__(
        self,
        k1: int = 10,
        k2: int = 3,
        pid_limit: int = 20,                      # 키워드당 최대 논문 수
        sim_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",  # 유사도 계산 모델
        searcher: VectorKeywordSearcher = None 
    ):
        self.k1 = k1
        self.k2 = k2
        self.pid_limit = pid_limit
        self.extractor = TFIDFExtractor()
        # 유사도 계산용 임베딩 모델
        self.sim_model = SentenceTransformer(sim_model_name)
        # 전처리: 루트 키워드 벡터(나중에 업데이트)
        self.root_vector = None
        self.searcher = searcher 

    def build(
        self,
        root_kw: str,
        root_pids: List[str],
        graph_dict: Dict[str, Dict],
        paper_meta: Dict[str, Dict]
    ) -> Tuple[Dict, Dict[str, List[Tuple[str, float]]]]:

        # 루트 키워드 벡터 저장
        self.root_vector = self.sim_model.encode(root_kw, convert_to_numpy=True)

        # 1) hop1 / hop2 논문 ID 수집
        hop1 = []
        for pid in root_pids:
            hop1 += graph_dict.get(pid, {}).get("references", [])
        hop1 = list(dict.fromkeys(hop1))

        hop2 = []
        for pid1 in hop1:
            hop2 += graph_dict.get(pid1, {}).get("references", [])
        hop2 = [p for p in dict.fromkeys(hop2) if p not in root_pids and p not in hop1]

        # 2) abstract 텍스트 수집
        hop1_texts = [paper_meta[pid]["abstract"] for pid in hop1 if pid in paper_meta]
        hop2_texts = [paper_meta[pid]["abstract"] for pid in hop2 if pid in paper_meta]

        # 3) 키워드 추출 (TF-IDF) — now returns scores too
        hop1_kw_map = self.extractor.extract_bulk(hop1_texts, top_n=self.k1)
        hop2_kw_map = self.extractor.extract_bulk(hop2_texts, top_n=self.k2)

        # 4) 그래프 및 kw2pids 생성
        nodes, links = [], []
        # { kw: [(pid, score), ...] }
        kw2pids: Dict[str, List[Tuple[str, float]]] = {}

        # 루트 노드
        nodes.append({"id": root_kw, "depth": 0, "sim": 1.0})

        # 1-Hop 키워드 노드
        for pid, kws in zip(hop1, hop1_kw_map.values()):
            for kw, kw_score in kws:
                # 유사도(루트↔키워드)
                vec = self.sim_model.encode(kw, convert_to_numpy=True)
                sim = float((vec @ self.root_vector) / (np.linalg.norm(vec) * np.linalg.norm(self.root_vector)))

                nodes.append({"id": kw, "depth": 1, "sim": sim})
                links.append({"source": root_kw, "target": kw, "weight": sim})
                # pid 매핑 + tfidf 점수
                kw2pids.setdefault(kw, []).append((pid, kw_score))

        # 2-Hop 키워드 노드
        for pid, kws in zip(hop2, hop2_kw_map.values()):
            for kw, kw_score in kws:
                vec = self.sim_model.encode(kw, convert_to_numpy=True)
                sim = float((vec @ self.root_vector) / (np.linalg.norm(vec) * np.linalg.norm(self.root_vector)))

                nodes.append({"id": kw, "depth": 2, "sim": sim})
                links.append({"source": root_kw, "target": kw, "weight": sim})
                # hop1과 연결할 때 sim 사용 가능
                # ...
                kw2pids.setdefault(kw, []).append((pid, kw_score))

        # 5) pid_limit 적용 및 정렬
        for kw, pid_list in kw2pids.items():
            # tfidf 점수 기준 내림차순 정렬, 상위 pid_limit개 선택
            pid_list.sort(key=lambda x: x[1], reverse=True)

            # 2) 부족하면, 외부 검색기로 채우기 (FAISS 유사도 사용)
            if len(pid_list) < self.pid_limit and self.searcher is not None:
                needed = self.pid_limit - len(pid_list)
                extras: List[Tuple[str,float]] = self.searcher.search(kw, topk=self.pid_limit)
                for pid, sim in extras:
                    if pid not in {p for p,_ in pid_list}:
                        pid_list.append((pid, sim))
                    if len(pid_list) >= self.pid_limit:
                        break
            kw2pids[kw] = pid_list[: self.pid_limit]

        # 6) 중복 제거
        unique_nodes = { (n["id"], n["depth"]) : n for n in nodes }
        unique_links = { (l["source"], l["target"]) : l for l in links }

        graph_json = {
            "nodes": list(unique_nodes.values()),
            "links": list(unique_links.values())
        }

        return graph_json, kw2pids
