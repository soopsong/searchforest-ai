#!/usr/bin/env python3
"""
Step 2: embed abstract text for every node in graph_raw.gpickle
Outputs
  • indices/text_emb.npz   –  key = paper_id, value = np.ndarray(float32, 384)
  • indices/pid2idx.pkl    –  {paper_id: row_idx}  (후속 단계용)
"""
import pathlib, tqdm, networkx as nx, numpy as np, pickle, orjson
from sentence_transformers import SentenceTransformer

GRAPH_PATH = pathlib.Path("indices/graph_raw.gpickle")
OUT_EMB    = pathlib.Path("indices/text_emb.npz")
OUT_MAP    = pathlib.Path("indices/pid2idx.pkl")
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH      = 512                      # GPU=2-4 GB → 512; CPU → 64 추천

print("🔹 load graph …")
G = nx.read_gpickle(GRAPH_PATH)

print("🔹 collect abstract texts …")
pids, texts = [], []

# collect abstract texts …
for pid, data in G.nodes(data=True):
    abstract = data.get("abstract") or ""

    # 리스트(또는 리스트-오브-리스트) → 문자열
    if isinstance(abstract, list):
        if abstract and isinstance(abstract[0], list):          # [[sent1,sent2], [sent3]]
            abstract = " ".join(sum(abstract, []))
        else:                                         # ["sent1", "sent2", ...]
            abstract = " ".join(abstract)
    abstract = abstract.strip()

    if abstract:
        pids.append(pid)
        texts.append(abstract)

print(f"  {len(texts):,} / {G.number_of_nodes():,} nodes have abstract")

print("🔹 load SBERT model:", MODEL_NAME)
device_id = 0           # 0번 GPU
model = SentenceTransformer(MODEL_NAME, device=f"cuda:{device_id}")

def batched(seq, size):
    for i in range(0, len(seq), size):
        yield seq[i:i+size]

emb_list = []
for chunk in tqdm.tqdm(list(batched(texts, BATCH)), desc="encode"):
    vec = model.encode(chunk, normalize_embeddings=True, show_progress_bar=False)
    emb_list.append(vec.astype("float32"))

emb = np.vstack(emb_list)           # (N, 384)
print("  final shape:", emb.shape)

# 저장
np.savez_compressed(OUT_EMB, **{pid: v for pid, v in zip(pids, emb)})
pickle.dump({pid: i for i, pid in enumerate(pids)}, OUT_MAP.open("wb"))
print(f"✓ saved → {OUT_EMB}  /  {OUT_MAP}")
