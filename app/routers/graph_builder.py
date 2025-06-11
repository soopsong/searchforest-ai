from typing import Dict, List, Set, Tuple

class GraphBuilder:
    def __init__(self, k1:int, k2:int, top_n:int):
        self.k1, self.k2, self.top_n = k1, k2, top_n

    def build(
        self,
        root_kw: str,
        root_pids: List[str],
        graph_dict: Dict[str,Dict],
        paper_meta: Dict[str,Dict]
    ) -> Tuple[Dict, Dict[str, Set[str]]]:
        # build_2depth_kw_graph 함수 로직 재사용
        from .graph_utils import build_2depth_kw_graph_with_mapping
        return build_2depth_kw_graph_with_mapping(
            root_kw, root_pids[0], graph_dict, paper_meta, self.k1, self.k2, self.top_n
        )