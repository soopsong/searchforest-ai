import os
from typing import Dict, Tuple
from data_util.dataloader import ScisummGraphLoader
from data_util.config import Config


class GraphLoader:
    """
    GraphLoader wraps ScisummGraphLoader to load metadata and build a citation subgraph
    without relying on loader.graph_strut_dict (which isn't exposed).
    """
    def __init__(self, config: Config):
        """
        Args:
            cfg (Config): configuration object containing:
                - train_path: directory for JSONL files
                - train_file: train JSONL filename
                - test_file: test JSONL filename
                - n_hop: number of hops (e.g., 2)
                - max_neighbor_num: max neighbors per hop
                - setting: 'inductive' or 'transductive'
                - load_vocab: whether to load or build vocabulary
        """
        self.config = config
        self.loader = ScisummGraphLoader(setting=config.setting)

    def load_graph_and_meta(self, paths: Dict[str, str]) -> Tuple[Dict[str, dict], Dict[str, dict]]:
        """
        Load citation graph and paper metadata from given paths.

        :param paths: Dict with keys like 'train', 'val', 'test' and their JSONL file paths.
        :return: Tuple of (graph_dict, paper_meta)
            - graph_dict: { paper_id: { "references": [pid, ...] } }
            - paper_meta: { paper_id: { "title": str, "abstract": str } }
        """
        # 1) process datasets: load and tokenize, add graph_struct etc.
        datainfo, vocab = self.loader.process(paths, self.config, load_vocab_file=True)
        
        graph_dict: Dict[str, dict] = {}
        paper_meta: Dict[str, dict] = {}

        # 각 split(train/val/test)을 모두 합쳐 citation info와 메타 수집
        for split_name, dataset in datainfo.datasets.items():
            for ins in dataset:
                pid = ins["paper_id"]  # Instance에서 key로 접근
                # references 필드 접근 (없으면 빈 리스트)
                refs = ins["references"] if "references" in ins.fields else []
                graph_dict[pid] = {"references": refs}

                # title, abstract도 동일하게
                title = ins["title"] if "title" in ins.fields else ""
                abstract = ins["abstract"] if "abstract" in ins.fields else ""
                paper_meta[pid] = {
                    "title": title,
                    "abstract": abstract
                }


        return graph_dict, paper_meta
        

if __name__ == "__main__":
    cfg = Config()
    cfg.train_path = "data/extracted/inductive"
    cfg.train_file = "train.jsonl"
    cfg.test_file = "test.jsonl"
    cfg.setting = "inductive"
    cfg.mode = "test"
    cfg.load_vocab = True

    cfg.vocab_path = os.path.join(cfg.train_path, "vocab")

    # paths에는 JSONL만 전달
    paths = {
        "train": os.path.join(cfg.train_path, cfg.train_file),
        "test":  os.path.join(cfg.train_path, cfg.test_file),
    }

    loader = GraphLoader(cfg)
    graph_dict, paper_meta = loader.load_graph_and_meta(paths)
    print(f"Loaded {len(graph_dict)} papers")
    some_pid = next(iter(graph_dict))
    print(some_pid, graph_dict[some_pid], paper_meta[some_pid])
