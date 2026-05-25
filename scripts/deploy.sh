#!/bin/bash
set -e
echo "🚀 部署 MES 平台..."
cp .env.example .env.prod 2>/dev/null || true
docker compose -f infrastructure/docker/docker-compose.prod.yml pull
docker compose -f infrastructure/docker/docker-compose.prod.yml up --build -d
echo "✅ 部署完成 → http://localhost"
