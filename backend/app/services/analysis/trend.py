"""趋势分析 — 良率趋势/产出趋势/NG趋势"""
from datetime import date, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.station import StationSummary
from app.models.project import ProjectKeyStation


async def get_yield_trend(
    db: AsyncSession, project: str, station_name: str, days: int = 7, shift: str = "summary"
) -> list[dict]:
    """指定站点最近 N 天良率趋势"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    result = await db.execute(
        select(
            StationSummary.report_date,
            func.avg(StationSummary.yield_rate).label("avg_yield"),
            func.sum(StationSummary.ng_qty).label("total_ng"),
        ).where(
            StationSummary.project == project,
            StationSummary.station_name == station_name,
            StationSummary.shift == shift,
            StationSummary.report_date >= start_date,
            StationSummary.report_date <= end_date,
        ).group_by(StationSummary.report_date)
        .order_by(StationSummary.report_date)
    )
    return [
        {
            "date": str(r.report_date),
            "yield_rate_pct": round((r.avg_yield or 0) * 100, 2),
            "ng_qty": r.total_ng or 0,
        }
        for r in result.fetchall()
    ]


async def get_output_trend(
    db: AsyncSession, projects: list[str], days: int = 7, shift: str = "summary"
) -> dict[str, list]:
    """多专案产出趋势"""
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    result = await db.execute(
        select(
            StationSummary.report_date,
            StationSummary.project,
            func.sum(StationSummary.output_qty).label("total_output"),
        ).where(
            StationSummary.project.in_(projects),
            StationSummary.shift == shift,
            StationSummary.report_date >= start_date,
            StationSummary.report_date <= end_date,
            StationSummary.station_name == "OQC",  # 以 OQC 产出为准
        ).group_by(StationSummary.report_date, StationSummary.project)
        .order_by(StationSummary.report_date, StationSummary.project)
    )
    data: dict[str, list] = {p: [] for p in projects}
    for r in result.fetchall():
        if r.project in data:
            data[r.project].append({"date": str(r.report_date), "output": r.total_output or 0})
    return data
