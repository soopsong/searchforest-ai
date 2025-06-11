import os
from collections import defaultdict

from app.data_util.config import Config
from app.data_util.dataloader import ScisummGraphLoader
from sklearn.feature_extraction.text import TfidfVectorizer

import argparse
from app.data_util.logging import logger
import json


def set_up_data_and_graph(data_config):
    # 1) 2-Hop 설정
    data_config.n_hop            = 2        # 2-Depth
    data_config.max_neighbor_num = 64

    paths = {"train": os.path.join(data_config.train_path, data_config.train_file),
             "test": os.path.join(data_config.train_path, data_config.test_file)}

    # 2) Loader 초기화
    loader = ScisummGraphLoader(setting=data_config.setting)
    datainfo, vocab = loader.process(paths, data_config, data_config.load_vocab)

    graph_dict = loader.graph_strut_dict
    paper_meta = {
        pid: {"title": info.title, "abstract": info.abstract}
        for pid, info in datainfo['paper_meta'].items()
    }

    logger.info('-' * 10 + "set up data done!" + '-' * 10)

    return datainfo, vocab, graph_dict, paper_meta

def run_graph():
    datainfo, vocab, graph_dict, paper_meta = set_up_data_and_graph(config)

    # 2) 루트 키워드∙논문 ID 지정
    root_kw  = "graph neural network summarization"
    root_pid = "W12-2901"  

    # 3) 2-Depth 키워드 그래프 생성
    graph_json = build_2depth_kw_graph(
        root_kw, root_pid,
        graph_dict, paper_meta,
        k1=8, k2=6, top_n=10
    )

    # 4) 결과 출력
    print(json.dumps(graph_json, indent=2, ensure_ascii=False))


def extract_keywords(text, top_n=10):
    vec = TfidfVectorizer(stop_words='english',
                          ngram_range=(1,2),
                          max_features=5000)
    X = vec.fit_transform([text])
    arr = X.toarray().ravel()
    idx = arr.argsort()[-top_n:][::-1]
    return [vec.get_feature_names_out()[i] for i in idx]

def build_2depth_kw_graph(root_kw, root_pid, graph_dict, paper_meta,k1=8, k2=6, top_n=10):
    """
    root_kw      : 사용자가 입력한 키워드
    root_pid     : root 논문 id  (root_kw를 포함하는 논문)
    graph_dict   : ScisummGraphLoader.graph_strut_dict
    paper_meta   : paper_id ➜ {"abstract": "...", "title": "..."}
    embed        : M3E encode 함수
    k1, k2       : depth1, depth2 노드 수
    """

    G = {"nodes": [], "links": []}
    seen = set()

    def add_node(kw, depth):
        if kw not in seen:
            G["nodes"].append({"id": kw, "depth": depth})
            seen.add(kw)

    # 0-Depth
    add_node(root_kw, 0)

    # 1-Hop / 2-Hop 논문 집합
    hop1 = set(graph_dict[root_pid]["references"])
    hop2 = set()
    for p in hop1:
        hop2 |= set(graph_dict.get(p, {}).get("references", []))
    hop2 -= {root_pid}

    # 1-Depth 키워드
    score1 = defaultdict(int)
    for pid in hop1:
        kws = extract_keywords(paper_meta[pid]["abstract"], top_n)
        for kw in kws:
            score1[kw] += 1
    depth1 = sorted(score1, key=score1.get, reverse=True)[:k1]
    for kw in depth1:
        add_node(kw, 1)
        G["links"].append({"source": root_kw, "target": kw})

    # 2-Depth 키워드
    for kw1 in depth1:
        score2 = defaultdict(int)
        for pid in (hop1|hop2):
            kws = extract_keywords(paper_meta[pid]["abstract"], top_n)
            for kw in kws:
                score2[kw] += 1
        depth2 = sorted(score2, key=score2.get, reverse=True)[:k2]
        for kw2 in depth2:
            if kw2 in {root_kw, kw1}: continue
            add_node(kw2, 2)
            G["links"].append({"source": kw1, "target": kw2})

    return G

def str2bool(v):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Unsupported value encountered.')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Graph script")
    parser.add_argument("--load_vocab", default=True, type=str2bool)
    parser.add_argument("--dataset_dir", default=None, help="dataset directory")
    parser.add_argument("--test_file", default="test.jsonl", help="test set file name")
    parser.add_argument("--train_file", default="train.jsonl", help="train set file name")
    parser.add_argument("--vocab_file", default="vocab")
    parser.add_argument("--setting", default="inductive", choices=["transductive", "inductive"])
    args = parser.parse_args()


    
    # 1) Config 생성 & 데이터·그래프 세팅
    config = Config()

    config.train_path = args.dataset_dir if args.dataset_dir is not None else os.path.join("../../../../Downloads/SSN", args.setting)
    config.train_file = args.train_file
    config.test_path = args.dataset_dir if args.dataset_dir is not None else os.path.join("../../../../Downloads/SSN", args.setting)
    config.test_file = args.test_file
    config.setting    = args.setting
    config.load_vocab = args.load_vocab

    config.vocab_path = os.path.join(config.train_path, args.vocab_file)

    logger.info("------start mode test-------")

    run_graph()