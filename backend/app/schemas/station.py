from pydantic import BaseModel
from datetime import date
from decimal import Decimal


class StationSummaryOut(BaseModel):
    id: int
    report_date: date
    shift: str
    project: str
    station_name: str
    input_qty: int
    output_qty: int
    ng_qty: int
    yield_rate: Decimal
    material_yield: Decimal
    process_yield: Decimal
    model_config = {"from_attributes": True}


class DashboardKpi(BaseModel):
    total_input: int
    total_output: int
    total_ng: int
    yield_rate: float
    yield_rate_pct: float


class NgRankItem(BaseModel):
    station_name: str
    ng_qty: int
    input_qty: int
    yield_rate_pct: float


class TrendPoint(BaseModel):
    date: str
    yield_rate_pct: float
    ng_qty: int


class StationCardOut(BaseModel):
    station_name: str
    input_qty: int
    ng_qty: int
    yield_rate_pct: float
    status: str  # normal / warning / error
    show_ng: bool
    show_yield: bool
    show_trend: bool
