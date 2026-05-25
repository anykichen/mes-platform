# MES 自动报表分析系统 v2.0

> 制造数据自动采集 + 专案分析 + 关键站点监控平台

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | Next.js 14 + TypeScript + Tailwind CSS + Recharts |
| 后端 | FastAPI + SQLAlchemy + Alembic |
| 自动化 | Playwright (Chromium) |
| 数据处理 | Pandas + OpenPyXL |
| 数据库 | PostgreSQL 15（按月分区） + Redis |
| 定时任务 | APScheduler |
| 部署 | Docker Compose |

## 快速启动

```bash
# 1. 复制环境变量
cp .env.example .env
# 编辑 .env 填写 MES 地址、数据库密码等

# 2. 一键启动（开发模式）
make dev

# 3. 初始化数据库
make db-init

# 4. 访问
# Dashboard: http://localhost:3000
# API Docs:  http://localhost:8000/docs
```

## 目录结构

```
mes-platform/
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── api/v1/        # REST API 路由
│   │   ├── core/          # 配置、安全、日志
│   │   ├── db/            # 数据库连接、初始化
│   │   ├── models/        # SQLAlchemy ORM 模型
│   │   ├── schemas/       # Pydantic 数据验证
│   │   ├── services/
│   │   │   ├── mes/       # MES 自动化（Playwright）
│   │   │   ├── parser/    # Excel 解析（Pandas）
│   │   │   └── analysis/  # KPI 分析、趋势计算
│   │   └── tasks/         # 定时任务（APScheduler）
│   └── alembic/           # 数据库迁移
├── frontend/              # Next.js 前端
│   ├── app/               # App Router 页面
│   ├── components/        # 可复用组件
│   │   ├── charts/        # Recharts 图表
│   │   ├── common/        # 通用 UI 组件
│   │   └── layout/        # 布局组件
│   ├── lib/               # API 客户端、工具函数
│   └── types/             # TypeScript 类型定义
├── infrastructure/
│   ├── docker/            # Docker Compose 配置
│   ├── nginx/             # Nginx 反向代理
│   └── postgres/          # 数据库初始化脚本
└── scripts/               # 运维脚本
```

## 开发阶段

- [x] Phase 0: 项目结构
- [ ] Phase 1: MES 自动化
- [ ] Phase 2: Excel 解析
- [ ] Phase 3: 数据库系统
- [ ] Phase 4: 配置系统
- [ ] Phase 5: Dashboard
- [ ] Phase 6: 定时任务
- [ ] Phase 7: AI 分析（后续）
