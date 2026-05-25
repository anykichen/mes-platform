from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class KeyStationBase(BaseModel):
    station_name: str
    enabled: bool = True
    display_order: int = 99
    show_ng: bool = True
    show_yield: bool = True
    show_trend: bool = True


class KeyStationCreate(KeyStationBase):
    pass


class KeyStationUpdate(BaseModel):
    station_name: Optional[str] = None
    enabled: Optional[bool] = None
    display_order: Optional[int] = None
    show_ng: Optional[bool] = None
    show_yield: Optional[bool] = None
    show_trend: Optional[bool] = None


class KeyStationOut(KeyStationBase):
    id: int
    project_name: str
    created_at: datetime
    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    project_name: str
    enabled: bool = True
    display_order: int = 99
    show_in_dashboard: bool = True
    enable_trend: bool = True


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    enabled: Optional[bool] = None
    display_order: Optional[int] = None
    show_in_dashboard: Optional[bool] = None
    enable_trend: Optional[bool] = None


class ProjectOut(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = {"from_attributes": True}
