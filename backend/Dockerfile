FROM mes-backend-base:latest

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --break-system-packages -r requirements.txt && \
    pip install --no-cache-dir --break-system-packages aiomysql pymysql

COPY . .

EXPOSE 8000

ENTRYPOINT []
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
