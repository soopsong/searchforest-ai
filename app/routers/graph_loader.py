import os
from typing import Dict, Tuple

from app.data_util.config import Config
from app.data_util.dataloader import ScisummGraphLoader

class GraphLoader:
    """
    GraphLoader wraps ScisummGraphLoader to load metadata and build a citation subgraph.
    """
    def __init__(self, cfg: Config):
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
        self.cfg = cfg
        self.loader = ScisummGraphLoader(setting=cfg.setting)

    def load_meta(self) -> Tuple[object, object]:
        """
        Load train/test JSONL files and prepare metadata and vocabulary.

        Returns:
            datainfo: object containing paper_meta and other dataset info
            vocab: vocabulary object (if load_vocab=True)
        """
        paths = {
            "train": os.path.join(self.cfg.train_path, self.cfg.train_file),
            "test":  os.path.join(self.cfg.train_path, self.cfg.test_file)
        }
        datainfo, vocab = self.loader.process(paths, self.cfg, self.cfg.load_vocab)
        return datainfo, vocab

    def build_graph(self) -> Dict[str, Dict]:
        """
        Return the citation graph dictionary built by ScisummGraphLoader.

        Returns:
            graph_dict: mapping from paper_id to metadata dict including 'references'
        """
        return self.loader.graph_strut_dict

    def load_and_build(self) -> Tuple[object, object, Dict[str, Dict]]:
        """
        Convenience method: load metadata then build and return the citation graph.

        Returns:
            datainfo: metadata object
            vocab: vocabulary object
            graph_dict: citation graph dictionary
        """
        datainfo, vocab = self.load_meta()
        graph_dict = self.build_graph()
        return datainfo, vocab, graph_dict
