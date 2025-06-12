#!/usr/bin/env bash
set -euo pipefail

########################################
# 사용자 환경에 맞게 여기를 바꿔주세요 #
########################################

# 1) 논문 메타 JSON ({"P1": {"abstract": "...", "references": [...]}, ...})
PAPER_META_JSON="app/data/extracted/SSN/papers.SSN.jsonl"

# 2) abstract 폴더 (각 paper_id.txt 파일이 들어있는 디렉터리)
ABSTRACT_DIR="app/routers/paper_ids.txt"

# 3) 사용할 SentenceTransformer 모델
MODEL="moka-ai/m3e-base"

# 4) 키워드 추출 시 top-K
TOP_K=10

# 5) root 키워드 (여기부터 1-hop/2-hop 그래프 생성)
ROOT_KW="quantum"

# 6) 출력 그래프 파일
OUTPUT_GRAPH="full_network.graphml"

########################################
#  이하 스크립트 수정 불필요           #
########################################

echo "[1/4] 논문 요약 임베딩 & FAISS 인덱스 생성"
python app/routers/embed_papers.py \
     --tldr_dir "$ABSTRACT_DIR" \
     --index paper.index \
     --id_map paper_ids.txt \
     --model "$MODEL"

echo "[2/4] 키워드 임베딩 & FAISS 인덱스 생성"
python app/routers/embed_keywords.py \
     --keywords keywords.txt \
     --index keyword.index \
     --id_map keyword_ids.txt \
     --model moka-ai/m3e-base

echo "[3/4] 전체 네트워크 빌드 (키워드+공동인용)"
python - <<EOF
import json, networkx as nx
from app.routers.pipeline import build_full_network
from app.routers.searcher import VectorKeywordSearcher

# load meta
with open("$PAPER_META_JSON", "r") as f:
    paper_meta = json.load(f)

# init searcher
searcher = VectorKeywordSearcher(
    hf_model_name="$MODEL",
    index_path="keyword.index",
    id_map_path="keyword_ids.txt"
)

# build
G = build_full_network(
    paper_meta=paper_meta,
    abstract_dir="$ABSTRACT_DIR",
    searcher=searcher,
    top_k=$TOP_K,
    root_kw="$ROOT_KW"
)

# save
nx.write_graphml(G, "$OUTPUT_GRAPH")
print("[✓] Saved network to $OUTPUT_GRAPH")
EOF

echo "[4/4] 완료!"
