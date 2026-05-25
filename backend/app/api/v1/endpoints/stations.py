from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date
from app.db.session import get_db
from app.models.station import StationSummary
from app.schemas.station import StationSummaryOut

router = APIRouter(prefix="/stations", tags=["站点数据"])


@router.get("/", response_model=list[StationSummaryOut])
async def list_stations(
    project: str = Query(...),
    report_date: date = Query(default_factory=date.today),
    shift: str = Query(default="summary"),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(StationSummary)
        .where(
            StationSummary.project == project,
            StationSummary.report_date == report_date,
            StationSummary.shift == shift,
        )
        .order_by(StationSummary.station_name)
    )
    return result.scalars().all()


@router.get("/dates")
async def available_dates(
    project: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """返回该专案有数据的日期列表"""
    result = await db.execute(
        select(StationSummary.report_date)
        .where(StationSummary.project == project)
        .distinct()
        .order_by(StationSummary.report_date.desc())
        .limit(90)
    )
    return [str(r[0]) for r in result.fetchall()]
