from sqlalchemy import String, Boolean, Integer, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base
from datetime import datetime


class ProjectConfig(Base):
    __tablename__ = "project_config"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=99)
    show_in_dashboard: Mapped[bool] = mapped_column(Boolean, default=True)
    enable_trend: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # 关联的重点站点
    key_stations: Mapped[list["ProjectKeyStation"]] = relationship(
        "ProjectKeyStation", back_populates="project", cascade="all, delete-orphan"
    )


class ProjectKeyStation(Base):
    __tablename__ = "project_key_station"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_name: Mapped[str] = mapped_column(String(100), ForeignKey("project_config.project_name"), nullable=False, index=True)
    station_name: Mapped[str] = mapped_column(String(200), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=99)
    show_ng: Mapped[bool] = mapped_column(Boolean, default=True)
    show_yield: Mapped[bool] = mapped_column(Boolean, default=True)
    show_trend: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    project: Mapped["ProjectConfig"] = relationship(
        "ProjectConfig",
        back_populates="key_stations",
    )
