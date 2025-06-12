import pytest
import networkx as nx

from app.routers.co_citation import build_co_citation_graph

@pytest.fixture
def sample_meta():
    # P1 and P2 both cite C1, P1 and P3 both cite C2, so there should be edges P1–P2 and P1–P3
    return {
        "P1": {"references": ["C1", "C2"]},
        "P2": {"references": ["C1"]},
        "P3": {"references": ["C2"]}
    }

def test_build_co_citation_graph(sample_meta):
    G = build_co_citation_graph(sample_meta)

    # All papers should be nodes
    assert set(G.nodes) == {"P1", "P2", "P3"}

    # P1 & P2 share C1 → edge weight 1
    assert G.has_edge("P1", "P2")
    assert G["P1"]["P2"]["weight"] == 1

    # P1 & P3 share C2 → edge weight 1
    assert G.has_edge("P1", "P3")
    assert G["P1"]["P3"]["weight"] == 1

    # P2 & P3 don’t share any citations → no edge
    assert not G.has_edge("P2", "P3")
