FROM python:3.9-slim

WORKDIR /app

# 1. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. curl, tar, file 설치 + Huggingface 인증용 환경변수
ARG HUGGINGFACE_TOKEN
ENV HUGGINGFACE_TOKEN=${HUGGINGFACE_TOKEN}
RUN apt-get update && apt-get install -y curl tar file

# 3. 데이터 다운로드 먼저 (복사 전에!)
# 주의: 파일이 gzip이 아니면 그냥 -o json 파일로 받고 압축 해제 생략
RUN curl -L -H "Authorization: Bearer ${HUGGINGFACE_TOKEN}" \
    -o inductive_test_checkpoint_collected.tar.gz \
    https://huggingface.co/datasets/3hreetimes/searchforest-ai-dataset/resolve/main/inductive_test_checkpoint_collected.tar.gz

RUN tar -xzf inductive_test_checkpoint_collected.tar.gz && \
    rm inductive_test_checkpoint_collected.tar.gz

# 4. 코드 복사 (덮어쓰지 않도록 이후에)
COPY kw2pids.json ./
COPY Dockerfile ./
COPY main.py ./

# 5. 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]