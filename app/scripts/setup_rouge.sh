#!/usr/bin/env bash
# run_test.sh: 환경변수 설정 후 test_CGSum 실행 스크립트
# setup_rouge.sh: pyrouge 환경 변수 설정 및 실행 권한 부여 스크립트

# 1) pyrouge 설치 디렉터리 경로 설정
export PYROUGE_HOME_DIR="$(dirname "${BASH_SOURCE[0]}")/../tools/ROUGE-1.5.5"

echo "Setting PYROUGE_HOME_DIR to $PYROUGE_HOME_DIR"

# 2) pyrouge 패스 등록 (pyrouge_set_rouge_path가 설치되어 있어야 합니다)
if command -v pyrouge_set_rouge_path &> /dev/null; then
  pyrouge_set_rouge_path "$PYROUGE_HOME_DIR"
  echo "pyrouge path set successfully."
else
  echo "Warning: pyrouge_set_rouge_path command not found."
fi

# 3) 실행 권한 부여
if [ -f "$PYROUGE_HOME_DIR/ROUGE-1.5.5.pl" ]; then
  chmod +x "$PYROUGE_HOME_DIR/ROUGE-1.5.5.pl"
  echo "Granted execute permission to ROUGE-1.5.5.pl"
else
  echo "Error: ROUGE-1.5.5.pl not found at $PYROUGE_HOME_DIR"
  exit 1
fi

echo "Setup completed."
