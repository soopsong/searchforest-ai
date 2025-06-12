import pickle, numpy as np
import joblib

emb = joblib.load("indices/graph_emb.pkl")
print(len(emb), "vectors loaded")     # 예: 140801 vectors

pid, vec = next(iter(emb.items()))
print(pid, vec.shape, vec[:5])
# ('102498304', (128,), [ 0.02 … ])
