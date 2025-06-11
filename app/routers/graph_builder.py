# routers/graph_builder.py

import json
from typing import Dict, List, Set, Tuple

from routers.keyword_extractor import TFIDFExtractor


class GraphBuilder:
    """
    2-Depth 키워드 그래프 생성기.
    - root_kw: 루트 키워드 문자열
    - root_pids: 루트 논문 ID 리스트 (보통 1개)
    - graph_dict: paper_id -> {"references": [...]}
    - paper_meta: paper_id -> {"title": ..., "abstract": ...}
    - k1, k2: hop1, hop2 키워드 개수
    """

    def __init__(self, k1: int = 8, k2: int = 6):
        self.k1 = k1
        self.k2 = k2
        self.extractor = TFIDFExtractor()

    def build(self,
              root_kw: str,
              root_pids: List[str],
              graph_dict: Dict[str, Dict],
              paper_meta: Dict[str, Dict]
              ) -> Tuple[Dict, Dict[str, Set[str]]]:
        
        # 1) hop1 / hop2 논문 ID 수집
        hop1 = []
        for pid in root_pids:
            hop1.extend(graph_dict.get(pid, {}).get("references", []))
        hop1 = list(dict.fromkeys(hop1))  # 중복 제거, 순서 유지

        hop2 = []
        for pid1 in hop1:
            hop2.extend(graph_dict.get(pid1, {}).get("references", []))
        # root_pids 및 hop1 제외
        hop2 = [pid for pid in dict.fromkeys(hop2)
                if pid not in root_pids and pid not in hop1]

        # 2) abstract 텍스트 수집
        hop1_texts = [paper_meta[pid]["abstract"] for pid in hop1 if pid in paper_meta]
        hop2_texts = [paper_meta[pid]["abstract"] for pid in hop2 if pid in paper_meta]
        
        # 빈 문자열 및 공백-only 문서는 제외
        hop1_valid = [t for t in hop1_texts if t and t.strip()]
        hop2_valid = [t for t in hop2_texts if t and t.strip()]


        # 3) 키워드 추출 (TF-IDF)
        # hop1_kw_map = self.extractor.extract_bulk(hop1_texts, top_n=self.k1)
        # hop2_kw_map = self.extractor.extract_bulk(hop2_texts, top_n=self.k2)
        if hop1_valid:
            hop1_kw_map = self.extractor.extract_bulk(hop1_valid, top_n=self.k1)
        else:
            hop1_kw_map = {}
        
        if hop2_valid:
            hop2_kw_map = self.extractor.extract_bulk(hop2_valid, top_n=self.k2)
        else:
            hop2_kw_map = {}

        # 4) 그래프 JSON 및 kw2pids 매핑 생성
        nodes = []
        links = []
        kw2pids: Dict[str, Set[str]] = {}

        # 루트 노드
        nodes.append({"id": root_kw, "depth": 0})

        # 1-Hop 키워드 노드
        for pid, kws in zip(hop1, hop1_kw_map.values()):
            for kw in kws:
                # 노드 추가
                nodes.append({"id": kw, "depth": 1})
                # 링크: 루트 → 1-Hop 키워드
                links.append({"source": root_kw, "target": kw})

                # kw2pids 매핑
                kw2pids.setdefault(kw, set()).add(pid)

        # 2-Hop 키워드 노드
        for pid, kws in zip(hop2, hop2_kw_map.values()):
            for kw in kws:
                # 노드 추가
                nodes.append({"id": kw, "depth": 2})
                # 이 키워드가 속한 1-Hop 키워드들에 연결
                # (여기서는 단순히 루트와도 연결하거나, hop1 노드와 연결할 수도 있음)
                # 예시: 루트→2depth, hop1[i]→2depth
                links.append({"source": root_kw, "target": kw})
                for pid1 in hop1:
                    # 2depth 키워드가 이 pid1의 descendant라면
                    if pid in graph_dict.get(pid1, {}).get("references", []):
                        # hop1 키워드들 중 pid1의 키워드를 찾아서 연결
                        for kw1 in hop1_kw_map.get(paper_meta[pid1]["abstract"], []):
                            links.append({"source": kw1, "target": kw})

                # kw2pids 매핑
                kw2pids.setdefault(kw, set()).add(pid)

        # 중복 노드/링크 제거
        unique_nodes = { (n["id"], n["depth"]) : n for n in nodes }
        unique_links = { (l["source"], l["target"]) : l for l in links }

        graph_json = {
            "nodes": list(unique_nodes.values()),
            "links": list(unique_links.values())
        }

        # set -> list로 변환
        kw2pids_list = { kw: list(pids) for kw, pids in kw2pids.items() }

        return graph_json, kw2pids_list


if __name__ == "__main__":
    # 간단 테스트 예시
    import os
    from data_util.config import Config
    from routers.graph_loader import GraphLoader

    cfg = Config()
    cfg.train_path = "data/extracted/inductive"
    cfg.train_file = "train.jsonl"
    cfg.test_file = "test.jsonl"
    cfg.setting = "inductive"
    cfg.mode = "test"
    cfg.load_vocab = True
    cfg.vocab_path = os.path.join(cfg.train_path, "vocab")

    paths = {
        "train": os.path.join(cfg.train_path, cfg.train_file),
        "test":  os.path.join(cfg.train_path, cfg.test_file),
    }

    # 1) graph_loader로 citation graph 만들기
    loader = GraphLoader(cfg)
    graph_dict, paper_meta = loader.load_graph_and_meta(paths)

    # 2) GraphBuilder로 2-depth 키워드 그래프 생성
    builder = GraphBuilder(k1=5, k2=3)
    graph_json, kw2pids = builder.build(
        root_kw="quantum linear systems",
        root_pids=[next(iter(graph_dict))],  # 임의 루트
        graph_dict=graph_dict,
        paper_meta=paper_meta
    )


    from data_util.logging import logger
    # logger로 정보 기록
    logger.info("Generated 2-Depth Keyword Graph:")
    logger.info(json.dumps(graph_json, indent=2, ensure_ascii=False))
    logger.info("kw2pids mapping:")
    logger.info(json.dumps(kw2pids, indent=2, ensure_ascii=False))