from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class TaskLogOut(BaseModel):
    id: int
    task_name: str
    project: Optional[str]
    shift: Optional[str]
    status: str
    message: Optional[str]
    success_count: int
    failed_count: int
    error_message: Optional[str]
    duration_sec: Optional[int]
    started_at: datetime
    finished_at: Optional[datetime]
    model_config = {"from_attributes": True}


class SchedulerJobOut(BaseModel):
    id: str
    name: str
    next_run_time: Optional[datetime]
    enabled: bool
