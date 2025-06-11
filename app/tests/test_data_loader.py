# tests/test_data_loader.py
import pytest
from graph_loader import GraphLoader
from app.data_util.config import Config

# 더미 객체 정의
class DummyInfo:
    def __init__(self, title, abstract):
        self.title = title
        self.abstract = abstract

class DummyDataInfo:
    def __init__(self):
        # paper_meta는 { pid: Info } 형태여야 함
        self.paper_meta = {
            'A': DummyInfo('Title A', 'Abstract A'),
            'B': DummyInfo('Title B', 'Abstract B'),
        }

@pytest.fixture
def dummy_cfg(tmp_path):
    # 임시 디렉터리에 더미 파일 경로 세팅
    cfg = Config()
    cfg.train_path      = str(tmp_path)
    cfg.train_file      = 'train.jsonl'
    cfg.test_file       = 'test.jsonl'
    cfg.setting         = 'inductive'
    cfg.load_vocab      = False
    cfg.n_hop           = 2
    cfg.max_neighbor_num
    return cfg

def test_load_and_build_graph(monkeypatch, dummy_cfg):
    loader = GraphLoader(dummy_cfg)

    # 1) process() 콜을 가로채서 fake_datainfo, fake_vocab 리턴
    fake_datainfo = DummyDataInfo()
    fake_vocab    = {'dummy': 0}
    monkeypatch.setattr(loader.loader, 'process',
                        lambda paths, cfg, load_vocab: (fake_datainfo, fake_vocab))

    # 2) graph_strut_dict 설정
    loader.loader.graph_strut_dict = {
        'A': {'references': ['B']},
        'B': {'references': []}
    }

    # 3) load_and_build() 호출
    datainfo, vocab, graph_dict = loader.load_and_build()

    # 4) 검증
    assert datainfo is fake_datainfo
    assert vocab == fake_vocab
    assert 'A' in graph_dict and graph_dict['A']['references'] == ['B']
    assert 'B' in graph_dict and graph_dict['B']['references'] == []

    # 그리고 load_meta() 와 build_graph() 개별 호출도 테스트해 두어도 좋습니다.
