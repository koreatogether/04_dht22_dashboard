# ���� ��������
FROM python:3.9-slim as development

WORKDIR /app

# ���� ������ ��ġ
COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

# �ҽ� �ڵ� ����
COPY . .

# ���� ���� ����
CMD ["python", "src/python/backend/main.py"]

# � ��������
FROM python:3.9-slim as production

WORKDIR /app

# �ý��� ��Ű�� ��ġ
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# � �������� ��ġ
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# �ҽ� �ڵ� ����
COPY src/ ./src/

# ������ ���丮 ����
RUN mkdir -p /app/data

# ��Ʈ ����
EXPOSE 8000

# � ���� ����
CMD ["uvicorn", "src.python.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
