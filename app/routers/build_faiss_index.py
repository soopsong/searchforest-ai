# build_faiss_index.py

import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
from data_util.logging import logger

# 1) 설정: 데이터 경로
DATA_PATH    = "data/extracted/inductive"
TRAIN_FILE   = os.path.join(DATA_PATH, "train.jsonl")
TEST_FILE    = os.path.join(DATA_PATH, "test.jsonl")
IDX_OUT      = "indices/paper_ivf.index"
IDMAP_OUT    = "indices/paper_ids.txt"
EMB_MODEL    = "moka-ai/m3e-base"
EMB_BATCH    = 64
EMB_DIM      = 768   # moka-ai/m3e-base embedding dim
NLIST        = 100   # FAISS IVF 클러스터 수

# 2) paper_meta 로드
def load_papers(*files):
    papers = {}
    for fp in files:
        with open(fp, encoding='utf8') as f:
            for line in f:
                obj = json.loads(line)
                pid = obj["paper_id"]
                text = obj.get("abstract") or obj.get("title") or ""
                papers[pid] = text
    return papers

papers = load_papers(TRAIN_FILE, TEST_FILE)
logger.info(f"Loaded {len(papers)} papers.")

# 3) 임베딩 모델 로드 (GPU 사용)
model = SentenceTransformer(EMB_MODEL)
model = model.to("cuda")  # GPU로 모델 전체 이동

# 4) 벡터화 및 ID 매핑
pids = list(papers.keys())
texts = [papers[pid] for pid in pids]

vectors = []
total = len(texts)
for i in range(0, total, EMB_BATCH):
    batch = texts[i:i+EMB_BATCH]
    emb = model.encode(batch, convert_to_numpy=True)
    vectors.append(emb)
    # 진행률 로그
    done = i + len(batch)
    logger.info(f"[Embedding] {done}/{total} batches ({done/total*100:.1f}%)")
vectors = np.vstack(vectors).astype('float32')
logger.info(f"Computed embeddings array of shape: {vectors.shape}")

# 5) FAISS GPU 인덱스 구성 (GPU 전용)
logger.info("Building FAISS GPU index (requires faiss-gpu)...")
# 5.1 CPU IVF-flat 생성
cpu_index = faiss.IndexIVFFlat(faiss.IndexFlatL2(EMB_DIM), EMB_DIM, NLIST)

# 5.2 GPU 리소스 생성 및 CPU->GPU 인덱스 변환
res = faiss.StandardGpuResources()  
gpu_index = faiss.index_cpu_to_gpu(res, 0, cpu_index)

# 5.3 학습 및 추가
gpu_index.train(vectors)
gpu_index.add(vectors)

# 5.4 GPU 인덱스 → CPU 인덱스 변환 (저장용)
final_index = faiss.index_gpu_to_cpu(gpu_index)

os.makedirs(os.path.dirname(IDX_OUT), exist_ok=True)
faiss.write_index(final_index, IDX_OUT)
logger.info(f"FAISS index written to: {IDX_OUT}")

# 6) ID 맵 저장 (텍스트 형식)
os.makedirs(os.path.dirname(IDMAP_OUT), exist_ok=True)
with open(IDMAP_OUT, 'w') as f:
    for pid in pids:
        f.write(pid + "\n")
logger.info(f"Paper IDs written to: {IDMAP_OUT}")