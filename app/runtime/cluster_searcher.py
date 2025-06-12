# runtime/cluster_searcher.py
import faiss, numpy as np, json, pickle, pathlib
from sentence_transformers import SentenceTransformer

IDX_DIR = pathlib.Path("indices")
MODEL_NAME = "moka-ai/m3e-base"

# ── 데이터 로드 ──────────────────────────
index  = faiss.read_index(str(IDX_DIR / "cluster.index"))
cent   = np.load(IDX_DIR / "cluster_centroids.npy").astype("float32")
meta   = json.load(open(IDX_DIR / "cluster_meta.json"))
pid2i  = pickle.load(open(IDX_DIR / "pid2idx.pkl", "rb"))
labels = np.load(IDX_DIR / "cluster_labels.npy")

# cluster_id → [paper_id, …]
cluster2pids = {}
for pid, idx in pid2i.items():
    cid = int(labels[idx])          # 반드시 int
    cluster2pids.setdefault(cid, []).append(pid)

# ── SBERT 모델 (GPU 사용) ────────────────
model = SentenceTransformer(MODEL_NAME, device="cuda:0")

ALPHA = 1.0          # Step 04에서 사용한 비율과 동일
def search_clusters(query: str, topk: int = 5):
    """query → [(cid, sim), …]"""
    txt = model.encode([query], normalize_embeddings=True)[0]  # (384,)
    txt = txt.astype("float32") * ALPHA                       # 가중치

    g_zero = np.zeros(128, dtype="float32")                   # 그래프 0벡터
    q_vec  = np.concatenate([txt, g_zero])                    # (512,)

    # (선택) 최종 L2 정규화
    q_vec /= np.linalg.norm(q_vec) + 1e-9
    q_vec = q_vec.reshape(1, -1).astype("float32")

    D, I = index.search(q_vec, topk)
    return [(int(cid), float(sim)) for cid, sim in zip(I[0], D[0])]

