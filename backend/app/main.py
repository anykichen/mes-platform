from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.router import api_router
from app.tasks.scheduler import setup_scheduler

logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动
    logger.info(f"🚀 {settings.APP_NAME} 启动中...")
    setup_scheduler()
    yield
    # 关闭
    from app.services.mes.browser import close_browser
    await close_browser()
    logger.info("服务已关闭")


app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="制造数据自动采集 + 专案分析 + 关键站点监控平台",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 路由
app.include_router(api_router)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
