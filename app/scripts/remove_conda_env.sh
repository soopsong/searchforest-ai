#!/usr/bin/env bash
set -euo pipefail

# ./remove_conda_env.sh <env_name>

if [ $# -ne 1 ]; then
  echo "Usage: $0 <conda_env_name>"
  exit 1
fi

ENV_NAME="$1"

echo "삭제할 Conda 환경: ${ENV_NAME}"

# 환경이 존재하는지 확인
if conda env list | grep -qE "^\s*${ENV_NAME}\s"; then
  echo "환경이 존재합니다. 삭제를 진행합니다..."
  conda env remove -n "${ENV_NAME}"
  echo "환경 '${ENV_NAME}' 이(가) 삭제되었습니다."
else
  echo "환경 '${ENV_NAME}' 을(를) 찾을 수 없습니다."
  exit 1
fi
