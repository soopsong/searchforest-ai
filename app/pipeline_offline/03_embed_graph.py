#!/usr/bin/env python3
import pathlib, networkx as nx, joblib, numpy as np, tqdm

from node2vec import Node2Vec      # 🔸 변경 (nodevectors → node2vec)

GRAPH_PATH = pathlib.Path("indices/graph_raw.gpickle")
OUT_PATH   = pathlib.Path("indices/graph_emb.pkl")

print("🔹 load graph …")
G = nx.read_gpickle(GRAPH_PATH)
print(f"  nodes={G.number_of_nodes():,}   edges={G.size():,}")

# ── Node2Vec 파라미터 (node2vec 0.4.4 API) ──
node2vec = Node2Vec(
    G,
    dimensions=128,
    walk_length=40,
    num_walks=20,
    workers=4,          # CPU 코어 수
)

print("🔹 train Node2Vec model …")
model = node2vec.fit(
    vector_size=128,
    window=10,
    min_count=1,
    batch_words=256,
)

print("🔹 extract embeddings …")
emb = {str(n): model.wv[str(n)].astype(np.float32) for n in G.nodes()}

OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
joblib.dump(emb, OUT_PATH)         # pickle보다 빠르고 용량 ↓
print(f"✓ saved → {OUT_PATH}   ({len(emb):,} vectors · 128-d)")
