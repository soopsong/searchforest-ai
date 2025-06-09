FROM python:3.9-slim

WORKDIR /app

# 1. 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y curl tar file beautifulsoup4

# 2. gdown 설치
RUN pip install gdown

# 3. Google Drive에서 파일 다운로드 (파일명은 확장자에 맞춰 수정해도 됨)
RUN gdown --id 1tFYFjScIyu9RvAHWWWf-SGHwTs7F5866 -O inductive_test_checkpoint_collected.tar.gz

RUN tar -xzf inductive_test_checkpoint_collected.tar.gz && \
    rm inductive_test_checkpoint_collected.tar.gz

# 4. 코드 복사 (덮어쓰지 않도록 이후에)
COPY kw2pids.json ./
COPY main.py ./

# 5. 앱 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]