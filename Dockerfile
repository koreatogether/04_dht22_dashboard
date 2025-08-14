# 개발 스테이지
FROM python:3.9-slim as development

WORKDIR /app

# 개발 의존성 설치
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# 소스 코드 복사
COPY . .

# 개발 서버 실행
CMD ["python", "src/python/backend/main.py"]

# 운영 스테이지
FROM python:3.9-slim as production

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 운영 의존성만 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ ./src/

# 데이터 디렉토리 생성
RUN mkdir -p /app/data

# 포트 노출
EXPOSE 8000

# 운영 서버 실행
CMD ["uvicorn", "src.python.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
