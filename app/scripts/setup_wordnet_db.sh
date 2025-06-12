#!/usr/bin/env bash
set -euo pipefail

# 수정: 접속할 원격 호스트/유저
REMOTE_USER="your_username"
REMOTE_HOST="your.host.address"

# 원격에서 ROUGE_HOME_DIR을 가리키는 변수
PYROUGE_HOME_DIR="/home/bruce.kim/searchforest-ai/app/tools/ROUGE-1.5.5"

ssh "${REMOTE_USER}@${REMOTE_HOST}" << 'EOF'
  set -euo pipefail

  cd "${PYROUGE_HOME_DIR}/data/WordNet-2.0-Exceptions/"
  echo "[INFO] Building WordNet exception DB..."
  ./buildExeptionDB.pl . exc WordNet-2.0.exc.db

  echo "[INFO] Creating symlink in parent directory..."
  cd ..
  ln -sf WordNet-2.0-Exceptions/WordNet-2.0.exc.db WordNet-2.0.exc.db

  echo "[INFO] Done."
EOF
