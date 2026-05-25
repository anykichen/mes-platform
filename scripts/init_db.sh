#!/bin/bash
set -e
echo "🔧 初始化 MES 平台数据库..."
docker compose -f infrastructure/docker/docker-compose.yml exec backend \
  sh -c "alembic upgrade head && python -m app.db.init_db"
echo "✅ 数据库初始化完成"
