FROM python:3.12-slim AS builder

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 복사
COPY . .

EXPOSE 5000

# Flask 앱 실행
CMD ["python", "app.py"]
