#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups"
mkdir -p $BACKUP_DIR
echo "📦 备份数据库 $DATE..."
docker compose -f infrastructure/docker/docker-compose.yml exec -T postgres \
  pg_dump -U ${POSTGRES_USER:-mes_user} ${POSTGRES_DB:-mes_platform} \
  | gzip > "$BACKUP_DIR/mes_platform_$DATE.sql.gz"
echo "✅ 备份完成: $BACKUP_DIR/mes_platform_$DATE.sql.gz"
# 保留最近 30 天备份
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
