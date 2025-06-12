import os
from typing import Dict, List, Set
import networkx as nx

# 1. Paper → Keyword 매핑 생성

def build_paper_keyword_map(
    summaries_dir: str,
    searcher,
    top_k: int = 10
) -> Dict[str, List[str]]:
    """
    각 paper_id에 대해 abstract를 FAISS로 검색하여 상위 top_k 키워드를 추출한 맵 생성
    summaries_dir: 각 paper_id.txt 파일(abstract)을 담은 디렉터리
    returns: { paper_id: [kw1, kw2, ...], ... }
    """
    mapping: Dict[str, List[str]] = {}
    for fname in sorted(os.listdir(summaries_dir)):
        if not fname.endswith('.txt'):
            continue
        pid = os.path.splitext(fname)[0]
        path = os.path.join(summaries_dir, fname)
        with open(path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        if not text:
            continue
        results = searcher.search(text, top_k)
        mapping[pid] = [kw for kw, _ in results]
    return mapping

# 2. Keyword → Paper 역인덱스 생성

def invert_index(paper_keywords: Dict[str, List[str]]) -> Dict[str, Set[str]]:
    """
    역인덱스 생성: 키워드 → 해당 키워드를 가진 paper_id 집합
    """
    inv: Dict[str, Set[str]] = {}
    for pid, kws in paper_keywords.items():
        for kw in kws:
            inv.setdefault(kw, set()).add(pid)
    return inv

# 3. GraphBuilder 리팩토링: 키워드 중심 흐름
class GraphBuilder:
    def __init__(
        self,
        paper_meta: Dict[str, Dict],            # { paper_id: {"abstract": ..., "references": [...]}, ... }
        inv_index: Dict[str, Set[str]]
    ):
        """
        paper_meta: 원본 메타데이터 (abstract, references 포함)
        inv_index: { keyword: set(paper_ids) }
        """
        self.paper_meta = paper_meta
        self.inv_index = inv_index
        self.graph = nx.DiGraph()

    def build(
        self,
        root_kw: str,
        root_pids: Set[str]
    ) -> nx.DiGraph:
        """
        root_kw: 사용자 매칭 키워드
        root_pids: 해당 키워드 포함 논문 ID 집합
        1-hop: root_pids
        2-hop: 각 1-hop 논문의 references
        텍스트: paper_meta[pid]['abstract'] 사용
        """
        # 0) 루트 키워드 노드 추가
        self.graph.add_node(root_kw, type='keyword')

        # 1) hop1 논문 노드 및 엣지 추가
        hop1 = root_pids
        for pid in hop1:
            self.graph.add_node(pid, type='paper', abstract=self.paper_meta.get(pid, {}).get('abstract', ''))
            self.graph.add_edge(root_kw, pid, depth=1)

        # 2) hop2 (references) 논문 노드 및 엣지 추가
        hop2: Set[str] = set()
        for pid in hop1:
            refs = set(self.paper_meta.get(pid, {}).get('references', []))
            hop2 |= refs

        for pid in hop2:
            self.graph.add_node(pid, type='paper', abstract=self.paper_meta.get(pid, {}).get('abstract', ''))
            # references 기반 방향 엣지
            for src in hop1:
                if pid in set(self.paper_meta.get(src, {}).get('references', [])):
                    self.graph.add_edge(src, pid, depth=2)
        return self.graph

# 4. 편의 함수

def build_keyword_graph(
    paper_meta: Dict[str, Dict],
    root_kw: str,
    root_pids: Set[str]
) -> nx.DiGraph:
    """
    주어진 root_kw와 root_pids로부터 키워드 중심 그래프 생성
    (abstract 키워드 맵 역인덱스는 외부에서 생성해야 함)
    """
    return GraphBuilder(paper_meta, inv_index=invert_index(
        {pid: pm.get('abstract_keywords', []) for pid, pm in paper_meta.items()}
    )).build(root_kw, root_pids)
