"""
APScheduler 定时任务配置
- 白班采集: 每天 20:05（白班结束后5分钟）
- 夜班采集: 每天 08:10（夜班结束后10分钟）
- 汇总采集: 每天 08:30
- Session保活: 每30分钟
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.tasks.collect_task import run_collect
from app.services.mes.session_manager import keepalive
from app.core.logging import setup_logging
from datetime import date

logger = setup_logging()
scheduler = AsyncIOScheduler(timezone="Asia/Bangkok")  # Auto_THA 时区


def setup_scheduler():
    # 白班采集（20:05 每日）
    scheduler.add_job(
        lambda: run_collect(date.today(), "day"),
        trigger=CronTrigger(hour=20, minute=5),
        id="collect_day",
        name="白班数据采集",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=300,
    )

    # 夜班采集（08:10 每日）
    scheduler.add_job(
        lambda: run_collect(date.today(), "night"),
        trigger=CronTrigger(hour=8, minute=10),
        id="collect_night",
        name="夜班数据采集",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=300,
    )

    # 汇总采集（08:30 每日）
    scheduler.add_job(
        lambda: run_collect(date.today(), "summary"),
        trigger=CronTrigger(hour=8, minute=30),
        id="collect_summary",
        name="汇总数据采集",
        replace_existing=True,
        max_instances=1,
        misfire_grace_time=600,
    )

    # Session 保活（每30分钟）
    scheduler.add_job(
        keepalive,
        trigger=CronTrigger(minute="*/30"),
        id="session_keepalive",
        name="MES Session 保活",
        replace_existing=True,
        max_instances=1,
    )

    scheduler.start()
    logger.info("定时任务调度器已启动")
    return scheduler
