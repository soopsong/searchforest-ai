FROM python:3.9-slim

WORKDIR /app

# 1. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y tar

# 2. gdown 설치
RUN pip install gdown beautifulsoup4

# 3. Google Drive에서 tar.gz 파일 다운로드 → data/ 안에 저장
RUN mkdir -p data && \
    gdown --id 1tFYFjScIyu9RvAHWWWf-SGHwTs7F5866 -O data/inductive_test_checkpoint_collected.tar.gz

# 2. data/ 폴더 안에서 압축 해제 + 압축 파일 삭제
RUN tar -xzf data/inductive_test_checkpoint_collected.tar.gz -C data/ && \
    rm data/inductive_test_checkpoint_collected.tar.gz

# 4. 코드 복사 (덮어쓰지 않도록 이후에)
COPY data/kw2pids.json ./
COPY main.py ./

# 5. 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]