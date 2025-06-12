#!/usr/bin/env python3
"""
Alternative Step 05: Faiss K-means clustering on 512-d embeddings
Outputs
  • indices/cluster_labels.npy   –  np.ndarray(int32) [N]  (same as Leiden file)
"""

import numpy as np, faiss, pathlib, argparse, os, tqdm

# ────────────── CLI / 기본 파라미터 ──────────────
p = argparse.ArgumentParser()
p.add_argument("--embed", default="indices/paper_embed.npy")
p.add_argument("--out",   default="indices/cluster_labels.npy")
p.add_argument("-k", "--clusters", type=int, default=4000,
               help="number of clusters (≈ 1 cluster / 35 papers)")
p.add_argument("--gpu", action="store_true",
               help="use GPU 0 if available")
args = p.parse_args()

EMB_PATH  = pathlib.Path(args.embed)
LABEL_OUT = pathlib.Path(args.out)
N_CLUST   = args.clusters
GPU       = args.gpu
# ────────────────────────────────────────────────

print("🔹 load embeddings …")
emb = np.load(EMB_PATH).astype('float32')        # (N, 512)
d   = emb.shape[1]

# 1) Faiss K-means ---------------------------------
print(f"🔹 run Faiss K-means  (k={N_CLUST}, gpu={GPU}) …")
km = faiss.Kmeans(d, N_CLUST, niter=20, verbose=True, gpu=GPU)
km.train(emb)

# 2) assign points → labels ------------------------
print("🔹 assign points …")
D, I = km.index.search(emb, 1)                   # I: (N,1)
labels = I.reshape(-1).astype("int32")

# 3) save ------------------------------------------
LABEL_OUT.parent.mkdir(parents=True, exist_ok=True)
np.save(LABEL_OUT, labels)
print(f"✓ {N_CLUST:,} clusters  →  {LABEL_OUT}")
