"""KPI 计算服务 — 今日投入/产出/良率/达成率"""
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.station import StationSummary


async def get_daily_kpi(db: AsyncSession, project: str, report_date: date, shift: str = "summary") -> dict:
    result = await db.execute(
        select(
            func.sum(StationSummary.input_qty).label("total_input"),
            func.sum(StationSummary.output_qty).label("total_output"),
            func.sum(StationSummary.ng_qty).label("total_ng"),
        ).where(
            StationSummary.project == project,
            StationSummary.report_date == report_date,
            StationSummary.shift == shift,
            StationSummary.station_name == "OQC"
        )
    )
    row = result.first()
    total_input = row.total_input or 0
    total_output = row.total_output or 0
    total_ng = row.total_ng or 0
    yield_rate = round((total_output / total_input) if total_input > 0 else 0, 4)

    return {
        "total_input": total_input,
        "total_output": total_output,
        "total_ng": total_ng,
        "yield_rate": yield_rate,
        "yield_rate_pct": round(yield_rate * 100, 2),
    }
