# tests/test_graph_builder.py
import pytest
import networkx as nx

from app.routers.graph_builder import GraphBuilder, build_paper_keyword_map, invert_index

class DummySearcher:
    def search(self, text, top_k):
        # return two dummy keywords for any text
        return [("foo", 1.0), ("bar", 0.9)]

@pytest.fixture
def abstract_dir(tmp_path):
    # create two dummy abstract files
    d = tmp_path / "abstracts"
    d.mkdir()
    (d / "P1.txt").write_text("This is paper one.")
    (d / "P2.txt").write_text("This is paper two.")
    return str(d)

def test_build_and_invert_and_builder(abstract_dir):
    # 1) build_paper_keyword_map & invert_index
    searcher = DummySearcher()
    pk = build_paper_keyword_map(abstract_dir, searcher, top_k=2)
    assert pk == {"P1": ["foo", "bar"], "P2": ["foo", "bar"]}

    ki = invert_index(pk)
    # each keyword maps to both papers
    assert ki["foo"] == {"P1", "P2"}
    assert ki["bar"] == {"P1", "P2"}

    # 2) GraphBuilder build
    # simulate paper_meta with references: P1 -> P2, P2 -> none
    paper_meta = {
        "P1": {"abstract": "...", "references": ["P2"]},
        "P2": {"abstract": "...", "references": []}
    }
    gb = GraphBuilder(paper_meta, ki)
    G = gb.build(root_kw="foo", root_pids=ki.get("foo", set()))

    # nodes: keyword + both papers + P2 referenced
    assert set(G.nodes) == {"foo", "P1", "P2"}

    # 1-hop edges: foo->P1 and foo->P2
    assert G.has_edge("foo", "P1") and G["foo"]["P1"]["depth"] == 1
    assert G.has_edge("foo", "P2") and G["foo"]["P2"]["depth"] == 1

    # 2-hop: P1->P2 (since P1 references P2)
    assert G.has_edge("P1", "P2") and G["P1"]["P2"]["depth"] == 2
    # and P2 has no outgoing depth-2 edges
    assert not any((u == "P2" and G.edges[u, v]["depth"] == 2) for u, v in G.edges)
