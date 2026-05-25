.PHONY: dev prod down db-init db-migrate db-reset logs ps clean

# 开发环境启动
dev:
	docker compose -f infrastructure/docker/docker-compose.yml up --build -d
	@echo "✅ 开发环境已启动"
	@echo "   Dashboard: http://localhost:3000"
	@echo "   API Docs:  http://localhost:8000/docs"

# 生产环境
prod:
	docker compose -f infrastructure/docker/docker-compose.prod.yml up --build -d

# 停止
down:
	docker compose -f infrastructure/docker/docker-compose.yml down

# 初始化数据库（建表 + 分区 + 种子数据）
db-init:
	docker compose -f infrastructure/docker/docker-compose.yml exec backend \
	  python -m app.db.init_db

# 运行 Alembic 迁移
db-migrate:
	docker compose -f infrastructure/docker/docker-compose.yml exec backend \
	  alembic upgrade head

# 重置数据库（危险！仅开发用）
db-reset:
	docker compose -f infrastructure/docker/docker-compose.yml exec backend \
	  alembic downgrade base
	$(MAKE) db-migrate

# 查看日志
logs:
	docker compose -f infrastructure/docker/docker-compose.yml logs -f

# 查看容器状态
ps:
	docker compose -f infrastructure/docker/docker-compose.yml ps

# 清理
clean:
	docker compose -f infrastructure/docker/docker-compose.yml down -v --rmi local
