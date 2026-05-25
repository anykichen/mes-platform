from sqlalchemy import String, DateTime, Text, func, Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
from datetime import datetime
from typing import Optional


class TaskLog(Base):
    __tablename__ = "task_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    task_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    project: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    shift: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # SUCCESS / ERROR / WARN / RUNNING
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    success_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    failed_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_sec: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
