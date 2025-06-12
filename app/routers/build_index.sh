#!/usr/bin/env bash
# build_index.sh
# Usage: ./build_index.sh keywords.txt keyword.index keyword_ids.txt

set -euo pipefail

KEYWORDS_FILE="${1:-keywords.txt}"
INDEX_FILE="${2:-keyword.index}"
ID_MAP_FILE="${3:-keyword_ids.txt}"
MODEL_NAME="moka-ai/m3e-base"

echo "[1] Encoding and indexing keywords from $KEYWORDS_FILE"
python embed_keywords.py \
  --keywords "$KEYWORDS_FILE" \
  --index "$INDEX_FILE" \
  --id_map "$ID_MAP_FILE" \
  --model "$MODEL_NAME"

echo "[✓] FAISS index: $INDEX_FILE"
echo "[✓] Keyword ID map: $ID_MAP_FILE"
