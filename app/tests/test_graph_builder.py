# test/test_graph_builder.py
import pytest
import networkx as nx

from app.routers.graph_builder import (
    build_paper_keyword_map,
    invert_index,
    build_keyword_graph,
)

@pytest.fixture
def sample_data(tmp_path):
    # 1) 임시 요약 파일 2개 만들기
    d = tmp_path / "tldr"
    d.mkdir()
    (d / "P1.txt").write_text("quantum variational algorithm")
    (d / "P2.txt").write_text("classical machine learning")
    return str(d)

class DummySearcher:
    # 요약 → 고정 키워드 매핑
    def search(self, text, top_k):
        if "quantum" in text:
            return [("quantum", 0.9), ("variational", 0.8)]
        else:
            return [("classical", 0.9), ("learning", 0.8)]


def test_build_and_invert_and_graph(sample_data):
    searcher = DummySearcher()
    # 1) 논문→키워드 맵
    pk = build_paper_keyword_map(sample_data, searcher, top_k=2)
    assert pk == {
        "P1": ["quantum", "variational"],
        "P2": ["classical", "learning"],
    }

    # 2) 키워드→논문 반전
    ki = invert_index(pk)
    assert ki["quantum"] == {"P1"}
    assert ki["learning"] == {"P2"}

    # 3) 그래프 생성
    G = build_keyword_graph(pk, ki)
    # 노드 검사
    assert set(G.nodes) == {"P1", "P2"}
    # 엣지는 공유 키워드 있을 때만 생성되므로 서로 다른 키워드만 가져서 엣지는 없음
    assert G.number_of_edges() == 0

    # 이제 공유 키워드가 하나라도 생기도록 pk 를 바꿔서 엣지 테스트
    pk2 = {"P1": ["foo", "bar"], "P2": ["bar", "baz"], "P3": ["foo"]}
    ki2 = invert_index(pk2)
    G2 = build_keyword_graph(pk2, ki2)
    # P1-P2 는 "bar" 공유 → 엣지 존재
    assert G2.has_edge("P1", "P2")
    assert G2["P1"]["P2"]["weight"] == 1
    assert G2["P1"]["P2"]["keywords"] == ["bar"]

    # P1-P3 는 "foo" 공유 → 엣지 존재
    assert G2.has_edge("P1", "P3")
    assert G2["P1"]["P3"]["weight"] == 1
    assert G2["P1"]["P3"]["keywords"] == ["foo"]
