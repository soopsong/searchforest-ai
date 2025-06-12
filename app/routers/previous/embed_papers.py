#!/usr/bin/env python3
# embed_papers.py

import os
import argparse
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def main(tldr_dir: str, index_path: str, id_map_path: str, model_name: str):
    # 1) 논문 요약 로드 (파일명 → paper_id 매핑)
    paper_ids = []
    summaries = []
    for fname in sorted(os.listdir(tldr_dir)):
        if not fname.endswith(".txt"):
            continue
        pid = os.path.splitext(fname)[0]  # e.g. "Model.A.0" → paper_id
        path = os.path.join(tldr_dir, fname)
        with open(path, "r", encoding="utf-8") as f:
            txt = f.read().strip()
            if not txt:
                continue
        paper_ids.append(pid)
        summaries.append(txt)
    print(f"[1] Loaded {len(summaries)} summaries from {tldr_dir!r}")

    # 2) 임베딩 계산 + L2 정규화
    print("[2] Loading SentenceTransformer and encoding summaries...")
    model = SentenceTransformer(model_name)
    embeddings = model.encode(summaries, convert_to_numpy=True).astype('float32')
    faiss.normalize_L2(embeddings)

    # 3) FAISS 인덱스 생성 (Inner Product)
    dim = embeddings.shape[1]
    print(f"[3] Building FAISS index (dim={dim})...")
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    # 4) 인덱스 및 ID 맵 저장
    print(f"[4] Saving index to {index_path!r} and id map to {id_map_path!r}...")
    faiss.write_index(index, index_path)
    with open(id_map_path, "w", encoding="utf-8") as f:
        for pid in paper_ids:
            f.write(pid + "\n")

    print("[✓] Done.")

if __name__ == "__main__":
    p = argparse.ArgumentParser(
        description="Encode paper summaries and build FAISS index"
    )
    p.add_argument(
        "--tldr_dir",
        required=True,
        help="Directory of .txt summaries (one file per paper, named <paper_id>.txt)"
    )
    p.add_argument(
        "--index",
        default="paper.index",
        help="Output FAISS index file"
    )
    p.add_argument(
        "--id_map",
        default="paper_ids.txt",
        help="Output paper ID map (one paper_id per line)"
    )
    p.add_argument(
        "--model",
        default="moka-ai/m3e-base",
        help="SentenceTransformer model name"
    )
    args = p.parse_args()

    main(
        tldr_dir=args.tldr_dir,
        index_path=args.index,
        id_map_path=args.id_map,
        model_name=args.model
    )
