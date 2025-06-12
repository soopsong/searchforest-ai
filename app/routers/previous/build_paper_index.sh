#!/usr/bin/env bash
# build_paper_index.sh
# Usage: ./build_paper_index.sh /absolute/path/to/pyrouge_root/system paper.index paper_ids.txt moka-ai/m3e-base

set -euo pipefail

TLDR_DIR="${1:?Please provide summary directory}"
INDEX_FILE="${2:-paper.index}"
ID_MAP_FILE="${3:-paper_ids.txt}"
MODEL_NAME="${4:-sentence-transformers/all-MiniLM-L6-v2}"

echo "[1] Encoding and indexing paper summaries from $TLDR_DIR"
python embed_papers.py \
  --tldr_dir "$TLDR_DIR" \
  --index "$INDEX_FILE" \
  --id_map "$ID_MAP_FILE" \
  --model "$MODEL_NAME"

echo "[✓] FAISS paper index: $INDEX_FILE"
echo "[✓] Paper ID map: $ID_MAP_FILE"
