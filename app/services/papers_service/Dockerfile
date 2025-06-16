FROM python:3.9-slim

# 1. 필수 패키지 + gdown 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends python3-pip git && \
    pip3 install --no-cache-dir gdown && \
    rm -rf /var/lib/apt/lists/*
# 2. 프로젝트 코드 복사
#    (컨텍스트 최상단에서 COPY . . 라면 /app 구조도 함께 포함됩니다)
WORKDIR /app
COPY . .

# 3. Google Drive에서 tar.gz 다운로드 → data/ 안에 저장·압축 해제
RUN mkdir -p app/data && \
    gdown --id 1ZKbW2ky1Fjz7-DFXh1wKiBsEkOI73IaX \
          -O app/data/paper_db.tar.gz && \
    tar -xzf app/data/paper_db.tar.gz \
        -C app/data && \
    rm  app/data/paper_db.tar.gz


# 4. 파이썬 의존성 설치
RUN pip3 install --no-cache-dir -r requirements.txt   # 경로는 필요에 맞게

# 5. 앱 실행
CMD ["uvicorn", "papers_service:app", "--host", "0.0.0.0", "--port", "8000"]