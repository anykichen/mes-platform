FROM mes-backend-base:latest

WORKDIR /app

# Install Playwright system deps (Chromium will be installed at container start)
RUN apt-get update -qq && \
    apt-get install -y -qq --no-install-recommends \
        libxdamage1 libxfixes3 libxrandr2 libgbm1 libxkbcommon0 libasound2 \
        libatspi2.0-0 libxcomposite1 libatk1.0-0 libatk-bridge2.0-0 \
        libcups2 libdrm2 libxshmfence1 libnss3 libnspr4 libxss1 \
        libgtk-3-0 libpango-1.0-0 libcairo2 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    pip install --no-cache-dir --break-system-packages aiomysql pymysql

COPY . .

EXPOSE 8000

ENTRYPOINT []
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
