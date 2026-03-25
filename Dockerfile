# 告訴系統怎麼安裝 Python 環境
# Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 複製並安裝依賴
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案原始碼
COPY . .