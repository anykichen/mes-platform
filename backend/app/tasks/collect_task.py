"""
数据采集任务
采集流程: 一个页面 → 一次设置（厂区/日期/时间）→ 逐专案查询导出 → Excel解析 → 入库

逻辑：
  ① 打开浏览器页面，登录 MES
  ② 导航到 MFG Daily → 设置厂区/日期/时间范围（只做一次）
  ③ 依次循环每个专案：
      设置专案名称 → 点击查询 → 检查数据 → 导出 Excel
      → 解析 Excel → 写入数据库（先删后插）→ 清理临时文件
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
    setup_mfg_daily_page,
    query_and_export_project,
    NoDataFoundError,
)
from app.services.mes.session_manager import create_fresh_page
from app.services.parser.transformer import excel_to_station_records
from app.core.logging import setup_logging

logger = setup_logging()


# ─── 数据库写入（带死锁重试）─────────────────────────────────
async def _save_to_db(
    project_name: str,
    report_date: date,
    shift: str,
    records: list,
) -> None:
    """先删除同专案+同日+同班次旧数据，再批量插入新数据"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with AsyncSessionLocal() as db:
                await db.execute(
                    delete(StationSummary).where(
                        StationSummary.project == project_name,
                        StationSummary.report_date == report_date,
                        StationSummary.shift == shift,
                    )
                )
                db.add_all(records)
                await db.commit()
            return
        except Exception as e:
            if "1213" in str(e) and attempt < max_retries - 1:
                logger.warning(
                    f"数据库死锁 [{project_name}]，第 {attempt+1} 次重试..."
                )
                await asyncio.sleep(1 + attempt * 0.5)
            else:
                raise


# ─── 主采集流程 ─────────────────────────────────────────────
async def run_collect(report_date: date = None, shift: str = "summary"):
    """
    串行采集所有启用专案：
      一个页面 → 一次初始化 → 逐专案查询导出 → 解析 → 入库
    """
    if report_date is None:
        report_date = date.today()

    start_time = time.time()
    task_name = f"collect_{shift}"
    log_id = await _start_log(task_name, shift=shift)

    # 获取所有启用专案
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

    total = len(projects)
    logger.info(f"共 {total} 个启用专案，开始串行采集")

    page = None
    results = []

    try:
        # ① 创建页面并登录
        page = await create_fresh_page()

        # ② 初始化 MFG Daily 页面（导航 + 厂区 + 日期 + 时间，只做一次）
        await setup_mfg_daily_page(page, report_date, shift)

        # ③ 逐专案采集
        for i, proj in enumerate(projects, 1):
            proj_name = proj.project_name
            logger.info(f"[{i}/{total}] 开始采集专案: {proj_name}")

            try:
                # 查询并导出 Excel
                filepath = await query_and_export_project(
                    page, proj_name, report_date, shift
                )

                # 解析 Excel → ORM 对象
                records = await excel_to_station_records(
                    filepath, proj_name, report_date
                )

                # 写入数据库
                await _save_to_db(proj_name, report_date, shift, records)

                # 清理临时文件
                if os.path.exists(filepath):
                    os.remove(filepath)

                logger.info(
                    f"[{i}/{total}] 专案 [{proj_name}] 采集完成，{len(records)} 条记录"
                )
                results.append({
                    "status": "success",
                    "name": proj_name,
                    "detail": f"{len(records)} 条记录",
                    "count": len(records),
                })

            except NoDataFoundError as e:
                logger.warning(f"[{i}/{total}] 专案 [{proj_name}] 无生产数据，跳过")
                results.append({
                    "status": "no_data",
                    "name": proj_name,
                    "detail": str(e),
                    "count": 0,
                })

            except Exception as e:
                error_msg = f"[{proj_name}] 失败: {e}"
                logger.error(f"[{i}/{total}] {error_msg}")
                results.append({
                    "status": "error",
                    "name": proj_name,
                    "detail": error_msg,
                    "count": 0,
                })

    except Exception as e:
        logger.error(f"采集任务异常中断: {e}")
        results.append({
            "status": "error",
            "name": "SYSTEM",
            "detail": f"任务中断: {e}",
            "count": 0,
        })

    finally:
        if page:
            try:
                await page.close()
            except Exception:
                pass

    # ─── 统计并记录日志 ─────────────────────────────────────
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
