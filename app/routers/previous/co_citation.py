# routers/co_citation.py
import networkx as nx
from typing import Dict, Set

def build_co_citation_graph(
    paper_meta: Dict[str, Dict]
) -> nx.Graph:
    """
    공동 인용 네트워크: 
    - 같은 논문 C를 인용한 모든 논문들 A,B 사이에 undirected edge 추가
    - edge weight는 “몇 개의 논문”을 같이 인용했는지 카운트
    """
    # 인용된 피인용 논문 → citing papers 집합
    cited_to_citers: Dict[str, Set[str]] = {}
    for pid, meta in paper_meta.items():
        for cited in meta.get("references", []):
            cited_to_citers.setdefault(cited, set()).add(pid)

    G = nx.Graph()
    # 각 피인용 논문 단위로 공동 인용 관계 구축
    for cited, citers in cited_to_citers.items():
        citers = list(citers)
        n = len(citers)
        for i in range(n):
            for j in range(i+1, n):
                a, b = citers[i], citers[j]
                if G.has_edge(a, b):
                    G[a][b]["weight"] += 1
                else:
                    G.add_edge(a, b, weight=1)
    return G
