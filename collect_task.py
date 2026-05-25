"""
数据采集任务
采集流程: MES导出 → Excel解析 → 入库
"""
import os
from datetime import date
from sqlalchemy import delete
from app.db.session import AsyncSessionLocal
from app.models.project import ProjectConfig
from app.models.station import StationSummary
from app.models.task_log import TaskLog
from app.services.mes.exporter import export_daily_report
from app.services.parser.transformer import excel_to_station_records
from app.core.logging import setup_logging
from sqlalchemy import select
import time

logger = setup_logging()


async def run_collect(report_date: date = None, shift: str = "summary"):
    """
    主采集任务
    - 遍历所有启用的专案
    - 每个专案导出 Excel → 解析 → 写入数据库
    """
    if report_date is None:
        report_date = date.today()

    start_time = time.time()
    task_name = f"collect_{shift}"
    log_id = await _start_log(task_name, shift=shift)

    async with AsyncSessionLocal() as db:
        # 获取所有启用的专案，按顺序
        result = await db.execute(
            select(ProjectConfig)
            .where(ProjectConfig.enabled == True)
            .order_by(ProjectConfig.display_order)
        )
        projects = result.scalars().all()

    if not projects:
        logger.warning("没有启用的专案，采集任务退出")
        await _finish_log(log_id, "WARN", "没有启用的专案", 0, 0)
        return

    success_count = 0
    error_msgs = []

    for proj in projects:
        try:
            logger.info(f"开始采集专案: {proj.project_name}")

            # 1. 导出 Excel
            filepath = await export_daily_report(proj.project_name, report_date, shift)

            # 2. 解析
            records = await excel_to_station_records(filepath, proj.project_name, report_date)

            # 3. 写入数据库（先删除当天同班次旧数据，再插入）
            async with AsyncSessionLocal() as db:
                await db.execute(
                    delete(StationSummary).where(
                        StationSummary.project == proj.project_name,
                        StationSummary.report_date == report_date,
                        StationSummary.shift == shift,
                    )
                )
                db.add_all(records)
                await db.commit()

            # 4. 清理临时文件
            if os.path.exists(filepath):
                os.remove(filepath)

            success_count += 1
            logger.info(f"专案 [{proj.project_name}] 采集完成，{len(records)} 条记录")

        except Exception as e:
            error_msg = f"[{proj.project_name}] 失败: {e}"
            error_msgs.append(error_msg)
            logger.error(error_msg)

    duration = int(time.time() - start_time)
    status = "SUCCESS" if not error_msgs else ("ERROR" if success_count == 0 else "WARN")
    msg = f"完成 {success_count}/{len(projects)} 个专案" + (f"，错误: {'; '.join(error_msgs)}" if error_msgs else "")
    failed_count = len(error_msgs)
    error_message = '; '.join(error_msgs) if error_msgs else None
    await _finish_log(log_id, status, msg, success_count, failed_count, error_message, duration)
    logger.info(f"采集任务完成: {msg} ({duration}s)")


async def _start_log(task_name: str, shift: str = None) -> int:
    async with AsyncSessionLocal() as db:
        log = TaskLog(
            task_name=task_name, 
            shift=shift, 
            status="RUNNING",
            success_count=0,
            failed_count=0
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log.id


async def _finish_log(log_id: int, status: str, message: str, success_count: int, failed_count: int, error_message: str = None, duration: int = None):
    from datetime import datetime
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(TaskLog).where(TaskLog.id == log_id))
        log = result.scalars().first()
        if log:
            log.status = status
            log.message = message
            log.success_count = success_count
            log.failed_count = failed_count
            log.error_message = error_message
            log.duration_sec = duration
            log.finished_at = datetime.utcnow()
            await db.commit()
