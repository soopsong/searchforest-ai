#!/usr/bin/env bash
# extract_keywords.sh
# Usage: ./extract_keywords.sh /path/to/pyrouge_root/system keywords.txt

set -euo pipefail

TLDR_DIR="${1:-/home/bruce.kim/searchforest-ai/app/scripts/pyrouge_root/20250611_192006/system}"
OUTPUT_PATH="${2:-keywords.txt}"
TOP_K=10000
MAX_DF=0.8
MIN_DF=5
MAX_FEATURES=50000

echo "[1] Reading summaries from: $TLDR_DIR"
echo "[2] Extracting top $TOP_K TF-IDF keywords..."
python extract_keywords.py \
  --tldr_dir "$TLDR_DIR" \
  --output "$OUTPUT_PATH" \
  --top_k "$TOP_K" \
  --max_df "$MAX_DF" \
  --min_df "$MIN_DF" \
  --max_features "$MAX_FEATURES"

echo "[✓] Keywords saved to: $OUTPUT_PATH"
