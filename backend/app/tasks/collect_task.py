"""
数据采集任务
采集流程: MES导出 → Excel解析 → 入库
支持并发采集，提升处理效率
"""
import os
import asyncio
import time
from datetime import date
from sqlalchemy import delete, select
from app.db.session import AsyncSessionLocal
from app.models.project import ProjectConfig
from app.models.station import StationSummary
from app.models.task_log import TaskLog
from app.services.mes.exporter import (
    export_daily_report_with_retry,
    NoDataFoundError,
)
from app.services.mes.session_manager import create_fresh_page
from app.services.parser.transformer import excel_to_station_records
from app.core.logging import setup_logging

logger = setup_logging()

# 最大并发采集数（每个并发会启动独立浏览器页面）
MAX_CONCURRENT = 3


async def _collect_single_project(
    proj: ProjectConfig,
    report_date: date,
    shift: str,
    semaphore: asyncio.Semaphore,
) -> dict:
    """
    采集单个专案（在信号量控制下并发执行）
    返回: {"status": "success"|"no_data"|"error", "name": str, "detail": str, "count": int}
    """
    async with semaphore:
        page = None
        try:
            logger.info(f"开始采集专案: {proj.project_name}")

            # 每个并发任务创建独立页面
            page = await create_fresh_page()

            # 1. 导出 Excel（带重试）
            filepath = await export_daily_report_with_retry(
                proj.project_name, report_date, shift, page=page
            )

            # 2. 解析
            records = await excel_to_station_records(
                filepath, proj.project_name, report_date
            )

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

            logger.info(
                f"专案 [{proj.project_name}] 采集完成，{len(records)} 条记录"
            )
            return {
                "status": "success",
                "name": proj.project_name,
                "detail": f"{len(records)} 条记录",
                "count": len(records),
            }

        except NoDataFoundError as e:
            logger.warning(f"专案 [{proj.project_name}] 无生产数据，跳过")
            return {
                "status": "no_data",
                "name": proj.project_name,
                "detail": str(e),
                "count": 0,
            }

        except Exception as e:
            error_msg = f"[{proj.project_name}] 失败: {e}"
            logger.error(error_msg)
            return {
                "status": "error",
                "name": proj.project_name,
                "detail": error_msg,
                "count": 0,
            }

        finally:
            if page:
                try:
                    await page.close()
                except Exception:
                    pass


async def run_collect(report_date: date = None, shift: str = "summary"):
    """
    主采集任务（并发版本）
    - 遍历所有启用的专案
    - 使用信号量控制并发数，每个专案独立导出 Excel → 解析 → 写入数据库
    """
    if report_date is None:
        report_date = date.today()

    start_time = time.time()
    task_name = f"collect_{shift}"
    log_id = await _start_log(task_name, shift=shift)

    async with AsyncSessionLocal() as db:
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

    # 并发采集所有专案
    semaphore = asyncio.Semaphore(MAX_CONCURRENT)
    tasks = [
        _collect_single_project(proj, report_date, shift, semaphore)
        for proj in projects
    ]
    results = await asyncio.gather(*tasks)

    # 统计结果
    success_count = 0
    no_data_count = 0
    error_msgs = []

    for r in results:
        if r["status"] == "success":
            success_count += 1
        elif r["status"] == "no_data":
            no_data_count += 1
        elif r["status"] == "error":
            error_msgs.append(r["detail"])

    duration = int(time.time() - start_time)

    # 构建状态和消息
    total = len(projects)
    if error_msgs:
        status = "ERROR" if success_count == 0 else "WARN"
    else:
        status = "SUCCESS"

    msg_parts = [f"完成 {success_count}/{total} 个专案"]
    if no_data_count > 0:
        msg_parts.append(f"{no_data_count} 个专案无数据")
    msg = "，".join(msg_parts)
    if error_msgs:
        msg += f"，错误: {'; '.join(error_msgs)}"

    failed_count = len(error_msgs)
    error_message = "; ".join(error_msgs) if error_msgs else None

    await _finish_log(
        log_id, status, msg, success_count, failed_count, error_message, duration
    )
    logger.info(f"采集任务完成: {msg} ({duration}s)")


async def _start_log(task_name: str, shift: str = None) -> int:
    async with AsyncSessionLocal() as db:
        log = TaskLog(
            task_name=task_name,
            shift=shift,
            status="RUNNING",
            success_count=0,
            failed_count=0,
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log.id


async def _finish_log(
    log_id: int,
    status: str,
    message: str,
    success_count: int,
    failed_count: int,
    error_message: str = None,
    duration: int = None,
):
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
