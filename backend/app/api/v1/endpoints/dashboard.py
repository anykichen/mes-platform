"""
Dashboard API
GET /api/v1/dashboard/kpi
GET /api/v1/dashboard/key-stations
GET /api/v1/dashboard/ng-rank
GET /api/v1/dashboard/yield-trend
GET /api/v1/dashboard/output-trend
GET /api/v1/dashboard/system-status
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import date, datetime
from app.db.session import get_db
from app.schemas.station import DashboardKpi, NgRankItem, TrendPoint, StationCardOut
from app.services.analysis.kpi import get_daily_kpi
from app.services.analysis.ng_rank import get_ng_rank
from app.services.analysis.trend import get_yield_trend, get_output_trend
from app.models.station import StationSummary
from app.models.project import ProjectKeyStation, ProjectConfig
from app.models.task_log import TaskLog
from app.models.account import MesAccount

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/kpi")
async def kpi(
    project: str = Query(...),
    report_date: date = Query(default_factory=date.today),
    shift: str = Query(default="summary"),
    db: AsyncSession = Depends(get_db),
):
    data = await get_daily_kpi(db, project, report_date, shift)
    return data


@router.get("/key-stations")
async def key_stations(
    project: str = Query(...),
    report_date: date = Query(default_factory=date.today),
    shift: str = Query(default="summary"),
    db: AsyncSession = Depends(get_db),
):
    """重点站点卡片数据"""
    ks_result = await db.execute(
        select(ProjectKeyStation)
        .where(
            ProjectKeyStation.project_name == project,
            ProjectKeyStation.enabled == True,
        )
        .order_by(ProjectKeyStation.display_order)
    )
    key_stations = ks_result.scalars().all()
    station_names = [ks.station_name for ks in key_stations]

    if not station_names:
        return []

    stats_result = await db.execute(
        select(
            StationSummary.station_name,
            func.sum(StationSummary.input_qty).label("input_qty"),
            func.sum(StationSummary.ng_qty).label("ng_qty"),
            func.avg(StationSummary.yield_rate).label("yield_rate"),
        ).where(
            StationSummary.project == project,
            StationSummary.report_date == report_date,
            StationSummary.shift == shift,
            StationSummary.station_name.in_(station_names),
        ).group_by(StationSummary.station_name)
    )
    stats = {r.station_name: r for r in stats_result.fetchall()}

    cards = []
    for ks in key_stations:
        s = stats.get(ks.station_name)
        yr = float(s.yield_rate or 0) * 100 if s else 0
        status = "normal" if yr >= 98 else ("warning" if yr >= 95 else "error")
        cards.append({
            "station_name": ks.station_name,
            "input_qty": int(s.input_qty or 0) if s else 0,
            "ng_qty": int(s.ng_qty or 0) if s else 0,
            "yield_rate_pct": round(yr, 2),
            "status": status,
            "show_ng": ks.show_ng,
            "show_yield": ks.show_yield,
            "show_trend": ks.show_trend,
        })
    return cards


@router.get("/ng-rank")
async def ng_rank(
    project: str = Query(...),
    report_date: date = Query(default_factory=date.today),
    shift: str = Query(default="summary"),
    top_n: int = Query(default=10),
    db: AsyncSession = Depends(get_db),
):
    return await get_ng_rank(db, project, report_date, shift, top_n)


@router.get("/yield-trend")
async def yield_trend(
    project: str = Query(...),
    station: str = Query(...),
    days: int = Query(default=7),
    shift: str = Query(default="summary"),
    db: AsyncSession = Depends(get_db),
):
    return await get_yield_trend(db, project, station, days, shift)


@router.get("/output-trend")
async def output_trend(
    projects: str = Query(..., description="逗号分隔的专案列表"),
    days: int = Query(default=7),
    shift: str = Query(default="summary"),
    db: AsyncSession = Depends(get_db),
):
    project_list = [p.strip() for p in projects.split(",")]
    return await get_output_trend(db, project_list, days, shift)


@router.get("/system-status")
async def system_status(db: AsyncSession = Depends(get_db)):
    """系统状态：MES连接、数据库、最近任务"""
    # 最近一次采集任务
    last_task = await db.execute(
        select(TaskLog)
        .where(TaskLog.task_name.like("collect_%"))
        .order_by(TaskLog.started_at.desc())
        .limit(1)
    )
    last = last_task.scalars().first()

    # MES 账号状态
    acc = await db.execute(select(MesAccount).limit(1))
    account = acc.scalars().first()

    return {
        "db_online": True,
        "mes_last_login_ok": account.last_login_ok if account else None,
        "mes_last_login_at": account.last_login_at if account else None,
        "last_collect_status": last.status if last else None,
        "last_collect_at": last.finished_at if last else None,
    }
