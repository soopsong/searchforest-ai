# routers/graph_builder.py

import json
import numpy as np
from typing import Dict, List, Tuple
from sentence_transformers import SentenceTransformer
from routers.keyword_extractor import TFIDFExtractor
from routers.searcher import VectorKeywordSearcher


class GraphBuilder:
    def __init__(
        self,
        k1: int = 10,
        k2: int = 3,
        pid_limit: int = 20,
        sim_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        searcher: VectorKeywordSearcher = None
    ):
        self.k1 = k1
        self.k2 = k2
        self.pid_limit = pid_limit
        self.extractor = TFIDFExtractor()
        self.sim_model = SentenceTransformer(sim_model_name)
        self.root_vector = None
        self.searcher = searcher

    def build(
        self,
        root_kw: str,
        root_pids: List[str],
        graph_dict: Dict[str, Dict],
        paper_meta: Dict[str, Dict]
    ) -> Tuple[Dict, Dict[str, List[Tuple[str, float]]]]:

        # 1) 루트 키워드 벡터 저장
        self.root_vector = self.sim_model.encode(root_kw, convert_to_numpy=True)

        # 2) Hop1/Hop2 논문 ID 수집
        hop1 = []
        for pid in root_pids:
            hop1 += graph_dict.get(pid, {}).get("references", [])
        hop1 = list(dict.fromkeys(hop1))

        hop2 = []
        for pid1 in hop1:
            hop2 += graph_dict.get(pid1, {}).get("references", [])
        hop2 = [p for p in dict.fromkeys(hop2) if p not in root_pids and p not in hop1]

        # 3) Abstract 수집
        hop1_texts = [paper_meta[pid]["abstract"] for pid in hop1 if pid in paper_meta]
        hop2_texts = [paper_meta[pid]["abstract"] for pid in hop2 if pid in paper_meta]

        # 4) TF-IDF 키워드 추출
        hop1_kw_map = self.extractor.extract_bulk(hop1_texts, top_n=self.k1)
        hop2_kw_map = self.extractor.extract_bulk(hop2_texts, top_n=self.k2)

        # 5) pid->keywords 매핑 생성
        hop1_pid_kws: Dict[str, List[Tuple[str, float]]] = {}
        for pid, kws in zip(hop1, hop1_kw_map.values()):
            hop1_pid_kws[pid] = kws

        hop2_pid_kws: Dict[str, List[Tuple[str, float]]] = {}
        for pid, kws in zip(hop2, hop2_kw_map.values()):
            hop2_pid_kws[pid] = kws

        # 6) 노드/링크 및 kw2pids 초기 생성
        nodes, links = [], []
        kw2pids: Dict[str, List[Tuple[str, float]]] = {}

        nodes.append({"id": root_kw, "depth": 0, "sim": 1.0})

        # 7) 1-Hop 처리
        for pid, kws in hop1_pid_kws.items():
            for kw, kw_score in kws:
                vec = self.sim_model.encode(kw, convert_to_numpy=True)
                sim = float((vec @ self.root_vector) / (np.linalg.norm(vec) * np.linalg.norm(self.root_vector)))
                nodes.append({"id": kw, "depth": 1, "sim": sim})
                links.append({"source": root_kw, "target": kw, "weight": sim})
                kw2pids.setdefault(kw, []).append((pid, kw_score))

        # 8) 2-Hop 처리 (루트→2depth 및 hop1→2depth)
        for pid, kws in hop2_pid_kws.items():
            for kw, kw_score in kws:
                vec = self.sim_model.encode(kw, convert_to_numpy=True)
                sim = float((vec @ self.root_vector) / (np.linalg.norm(vec) * np.linalg.norm(self.root_vector)))

                # depth=2 노드, 루트→2depth 간선
                nodes.append({"id": kw, "depth": 2, "sim": sim})
                links.append({"source": root_kw, "target": kw, "weight": sim})

                # hop1→2depth 간선 추가
                for pid1 in hop1:
                    if pid in graph_dict.get(pid1, {}).get("references", []):
                        for kw1, _ in hop1_pid_kws.get(pid1, []):
                            links.append({"source": kw1, "target": kw, "weight": sim})

                kw2pids.setdefault(kw, []).append((pid, kw_score))

        # 9) pid_limit 및 외부 보충
        for kw, pid_list in kw2pids.items():
            pid_list.sort(key=lambda x: x[1], reverse=True)
            if len(pid_list) < self.pid_limit and self.searcher:
                needed = self.pid_limit - len(pid_list)
                extras = self.searcher.search(kw, topk=self.pid_limit)
                for ext_pid, ext_sim in extras:
                    if ext_pid not in {p for p, _ in pid_list}:
                        pid_list.append((ext_pid, ext_sim))
                    if len(pid_list) >= self.pid_limit:
                        break
            kw2pids[kw] = pid_list[:self.pid_limit]

        print(len(hop1), len(hop2))


        # 10) 중복 제거
        unique_nodes = {(n['id'], n['depth']): n for n in nodes}
        unique_links = {(l['source'], l['target']): l for l in links}

        graph_json = {
            "nodes": list(unique_nodes.values()),
            "links": list(unique_links.values())
        }

        # 11) sim_scaled 계산 (1-Hop & 2-Hop)
        alpha = 5.0
        for depth in (1, 2):
            depth_nodes = [n for n in graph_json['nodes'] if n['depth'] == depth]
            sims = np.array([n['sim'] for n in depth_nodes], dtype=np.float32)
            exp_sims = np.exp(sims * alpha)
            softmax = exp_sims / exp_sims.sum()
            for n, s in zip(depth_nodes, softmax):
                n['sim_scaled'] = float(s)
                for l in graph_json['links']:
                    if l['target'] == n['id']:
                        l['weight_scaled'] = float(s)

        return graph_json, kw2pids
