#!/usr/bin/env bash
# monitor_gpu.sh: 실시간으로 GPU 상태를 모니터링하는 스크립트

# 기본 간격(1초)으로 모니터링
#./monitor_gpu.sh

# 5초 간격으로 모니터링
#./monitor_gpu.sh 5


# 갱신 간격(초)을 인자로 받을 수 있도록 기본값 설정
INTERVAL=${1:-1}

# nvidia-smi가 설치되어 있는지 확인
if ! command -v nvidia-smi &> /dev/null; then
  echo "Error: nvidia-smi 명령을 찾을 수 없습니다. NVIDIA 드라이버와 CUDA 툴킷이 설치되어 있는지 확인하세요."
  exit 1
fi

# watch 명령이 있는지 확인
if ! command -v watch &> /dev/null; then
  echo "Error: watch 명령을 찾을 수 없습니다. 설치 후 다시 시도하세요."
  exit 1
fi

# 모니터링 실행
echo "GPU 상태를 매 ${INTERVAL}초마다 갱신합니다. (종료: Ctrl+C)"
watch -n ${INTERVAL} nvidia-smi
