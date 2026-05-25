from sqlalchemy import String, Integer, Date, Numeric, DateTime, func, Index
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base
from datetime import date, datetime
from decimal import Decimal


class StationSummary(Base):
    """
    站点统计主表 — 每行 = 一个工站 × 一个班次 × 一天
    按 report_date 月份分区（在 PostgreSQL 中通过 partitions.sql 创建）
    """
    __tablename__ = "station_summary"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    report_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    shift: Mapped[str] = mapped_column(String(20), nullable=False)  # summary / day / night
    project: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False)
    input_qty: Mapped[int] = mapped_column(Integer, default=0)
    output_qty: Mapped[int] = mapped_column(Integer, default=0)
    ng_qty: Mapped[int] = mapped_column(Integer, default=0)
    yield_rate: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=0)       # 0.9880
    material_yield: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=0)
    process_yield: Mapped[Decimal] = mapped_column(Numeric(6, 4), default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    __table_args__ = (
        Index("ix_station_summary_date_project", "report_date", "project"),
        Index("ix_station_summary_date_station", "report_date", "station_name"),
    )
