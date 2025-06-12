# routers/pipeline.py
import networkx as nx

from .graph_builder import (
    build_paper_keyword_map,
    invert_index,
    build_keyword_graph,
)
from .co_citation import build_co_citation_graph
from .searcher import VectorKeywordSearcher  # 가정

def build_full_network(
    paper_meta: Dict[str, Dict],
    abstract_dir: str,
    searcher: VectorKeywordSearcher,
    top_k: int,
    root_kw: str
) -> nx.Graph:
    # 1) 논문별 키워드 맵 생성 (abstract → keywords)
    pk = build_paper_keyword_map(abstract_dir, searcher, top_k=top_k)

    # 2) 키워드→논문 역인덱스
    ki = invert_index(pk)

    # 3) root 키워드 기반 sub‐graph (1‐hop/2‐hop 인용 흐름)
    root_pids = ki.get(root_kw, set())
    G_kw = build_keyword_graph(paper_meta, root_kw, root_pids)

    # 4) 전체 공동 인용 그래프
    G_cc = build_co_citation_graph(paper_meta)

    # 5) 두 그래프 병합
    #    - 키워드 그래프 (DiGraph)와 공동 인용(undirected)을 합치려면 모두 간선 방향을 무시하고 합칠 수 있습니다.
    G_cc = G_cc.to_directed()  # 또는 nx.Graph 그대로 두고, 이후 합쳐도 OK
    G_full = nx.compose(G_kw, G_cc)

    return G_full


if __name__ == "__main__":
    from routers.pipeline import build_full_network
    # paper_meta 불러오기 예: {pid: {"abstract": "...", "references": [...]}, ...}
    G = build_full_network(
        paper_meta=paper_meta,
        abstract_dir="/path/to/abstract_txts",
        searcher=VectorKeywordSearcher(...),
        top_k=10,
        root_kw="quantum"
    )

