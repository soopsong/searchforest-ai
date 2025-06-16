# CUDA + Python 베이스 예시 (12.2, Py 3.10)
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    NVIDIA_VISIBLE_DEVICES=all

WORKDIR /app

# 필수 패키지
RUN apt-get update && apt-get install -y \
        python3-pip python3-dev git && \
    rm -rf /var/lib/apt/lists/*

# 1) requirements만 먼저 복사 → 레이어 캐시
COPY runtime/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 2) 실제 런타임 코드 복사
COPY runtime/ ./runtime/

# 지표·인덱스(volume 으로 붙여도 OK)
# COPY indices/ /workspace/indices

EXPOSE 8004
CMD ["uvicorn", "runtime.api:app", "--host", "0.0.0.0", "--port", "8004"]
