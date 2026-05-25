FROM python:3.11-slim-bookworm

WORKDIR /app

# 安装系统依赖 + Playwright 浏览器依赖
RUN apt-get update && apt-get install -y \
    wget curl gnupg \
    libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 \
    libxdamage1 libxfixes3 libxrandr2 libgbm1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY requirements.txt .
RUN pip install --no-cache-dir "sqlalchemy>=2.0,<2.0.30" && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir aiomysql pymysql

# 安装 Playwright Chromium
RUN playwright install chromium --with-deps

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
