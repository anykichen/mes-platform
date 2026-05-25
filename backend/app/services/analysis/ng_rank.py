"""NG 排行计算 — 只统计重点站点"""
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.station import StationSummary
from app.models.project import ProjectKeyStation


async def get_ng_rank(
    db: AsyncSession, project: str, report_date: date, shift: str = "summary", top_n: int = 10
) -> list[dict]:
    """返回重点站点按 NG 数量降序排列的列表"""
    # 获取重点站点列表
    ks_result = await db.execute(
        select(ProjectKeyStation.station_name)
        .where(
            ProjectKeyStation.project_name == project,
            ProjectKeyStation.enabled == True,
            ProjectKeyStation.show_ng == True,
        )
        .order_by(ProjectKeyStation.display_order)
    )
    key_stations = [r[0] for r in ks_result.fetchall()]
    if not key_stations:
        return []

    result = await db.execute(
        select(
            StationSummary.station_name,
            func.sum(StationSummary.ng_qty).label("total_ng"),
            func.sum(StationSummary.input_qty).label("total_input"),
            func.avg(StationSummary.yield_rate).label("avg_yield"),
        ).where(
            StationSummary.project == project,
            StationSummary.report_date == report_date,
            StationSummary.shift == shift,
            StationSummary.station_name.in_(key_stations),
        ).group_by(StationSummary.station_name)
        .order_by(func.sum(StationSummary.ng_qty).desc())
        .limit(top_n)
    )
    return [
        {
            "station_name": r.station_name,
            "ng_qty": r.total_ng or 0,
            "input_qty": r.total_input or 0,
            "yield_rate_pct": round((r.avg_yield or 0) * 100, 2),
        }
        for r in result.fetchall()
    ]
