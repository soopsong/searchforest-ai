#!/usr/bin/env bash
set -euo pipefail

# YAML 파일을 지정해 환경 생성
# ./create_conda_env.sh myenv environment.yml

# YAML 없이 기본 Python 환경만 생성
# ./create_conda_env.sh myenv

if [ $# -lt 1 ]; then
  echo "Usage: $0 <env_name> [environment_file.yml]"
  exit 1
fi

ENV_NAME="$1"
ENV_FILE="${2:-}"

if conda env list | grep -qE "^\s*${ENV_NAME}\s"; then
  echo "Environment '${ENV_NAME}' already exists. Exiting."
  exit 1
fi

if [ -n "$ENV_FILE" ]; then
  if [ ! -f "$ENV_FILE" ]; then
    echo "Specified environment file '$ENV_FILE' not found."
    exit 1
  fi
  echo "Creating Conda environment '${ENV_NAME}' from file '${ENV_FILE}'..."
  conda env create -n "$ENV_NAME" -f "$ENV_FILE"
else
  echo "Creating Conda environment '${ENV_NAME}' with default Python version..."
  conda create -y -n "$ENV_NAME" python
fi

echo "Environment '${ENV_NAME}' created successfully."