# Dockerfile
FROM nvcr.io/nvidia/cuda:10.0-cudnn7-devel-ubuntu18.04


ENV LANG=C.UTF-8


# Python 및 기타 기본 도구 설치
RUN apt-get update && apt-get install -y \
    python3.6 \
    python3.6-dev \
    python3-pip \
    git \
    curl \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/python3.6 /usr/bin/python

# pip 업그레이드
RUN python -m pip install --upgrade pip

# PyTorch 1.1.0 (CUDA 10.0) 설치
RUN pip install torch==1.1.0 torchvision==0.3.0

# 논문 요구 패키지 설치
RUN pip install \
    dgl==0.4.3 \
    fastNLP==0.5.0 \
    rouge==1.0.0 \
    pyrouge==0.1.3 \
    fastapi \
    uvicorn[standard] \
    pydantic \
    tqdm

# 작업 디렉토리 설정
WORKDIR /workspace
