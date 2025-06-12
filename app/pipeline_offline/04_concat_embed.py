#!/usr/bin/env python3
# pipeline_offline/04_concat_embed.py
"""
Merge 384-d SBERT text vectors + 128-d Node2Vec graph vectors
Outputs
  • indices/paper_embed.npy   –  np.ndarray(float32)  [N, 512]
  • indices/pid2idx.pkl       –  {paper_id: row_idx}
"""
import numpy as np, joblib, pickle, pathlib, tqdm, orjson

TEXT_PATH  = pathlib.Path("indices/text_emb.npz")
GRAPH_PATH = pathlib.Path("indices/graph_emb.pkl")
OUT_VEC    = pathlib.Path("indices/paper_embed.npy")
OUT_MAP    = pathlib.Path("indices/pid2idx.pkl")
ALPHA      = 0.7                     # 텍스트 70 %, 그래프 30 %

print("🔹 load text & graph embeddings …")
text_npz = np.load(TEXT_PATH)        # key = paper_id, value = (384,)
graph    = joblib.load(GRAPH_PATH)   # dict {paper_id: (128,)}

rows, pid2idx = [], {}
for pid in tqdm.tqdm(text_npz.files, desc="merge"):
    if pid not in graph:                 # 그래프 벡터 없는 논문 skip
        continue
    t = text_npz[pid]
    g = graph[pid]
    # L2 정규화 후 가중 합
    t /= np.linalg.norm(t) + 1e-9
    g /= np.linalg.norm(g) + 1e-9
    rows.append(np.concatenate([t*ALPHA, g*(1-ALPHA)]))
    pid2idx[pid] = len(rows)-1

embed = np.vstack(rows).astype("float32")
OUT_VEC.parent.mkdir(parents=True, exist_ok=True)
np.save(OUT_VEC, embed)
pickle.dump(pid2idx, OUT_MAP.open("wb"))
print(f"✓ saved → {OUT_VEC} ({embed.shape})  /  {OUT_MAP}")
