from fastapi import APIRouter, BackgroundTasks, Query
from datetime import date
from app.tasks.collect_task import run_collect
from app.tasks.scheduler import scheduler
from app.db.session import AsyncSessionLocal
from app.models.task_log import TaskLog
from app.schemas.task_log import TaskLogOut, SchedulerJobOut
from sqlalchemy import select

router = APIRouter(prefix="/tasks", tags=["定时任务"])


@router.post("/trigger")
async def trigger_collect(
    background_tasks: BackgroundTasks,
    shift: str = Query(default="summary"),
    report_date: date = Query(default_factory=date.today),
):
    """手动触发采集任务"""
    background_tasks.add_task(run_collect, report_date, shift)
    return {"message": f"采集任务已提交: {report_date} {shift}"}


@router.get("/logs", response_model=list[TaskLogOut])
async def get_logs(limit: int = Query(default=20)):
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(TaskLog).order_by(TaskLog.started_at.desc()).limit(limit)
        )
        return result.scalars().all()


@router.get("/jobs", response_model=list[SchedulerJobOut])
async def get_jobs():
    """获取所有定时任务状态"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time,
            "enabled": job.next_run_time is not None,
        })
    return jobs


@router.post("/jobs/{job_id}/pause")
async def pause_job(job_id: str):
    scheduler.pause_job(job_id)
    return {"ok": True}


@router.post("/jobs/{job_id}/resume")
async def resume_job(job_id: str):
    scheduler.resume_job(job_id)
    return {"ok": True}
