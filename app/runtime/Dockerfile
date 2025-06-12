# CUDA + Python 베이스 예시 (12.2, Py 3.10)
FROM nvidia/cuda:12.2.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    NVIDIA_VISIBLE_DEVICES=all

# 필수 패키지
RUN apt-get update && apt-get install -y \
        python3-pip python3-dev git && \
    rm -rf /var/lib/apt/lists/*

# 프로젝트 소스 복사
WORKDIR /workspace
COPY .. /workspace      

# 의존성(인퍼런스 전용)
RUN pip3 install --upgrade pip \
 && pip3 install -r app/runtime/requirements.txt

# 지표·인덱스(volume 으로 붙여도 OK)
# COPY indices/ /workspace/indices

EXPOSE 8004
CMD ["uvicorn", "app.runtime.api:app", "--host", "0.0.0.0", "--port", "8004"]