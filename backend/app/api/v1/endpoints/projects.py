from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.models.project import ProjectConfig, ProjectKeyStation
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut, KeyStationCreate, KeyStationUpdate, KeyStationOut

router = APIRouter(prefix="/projects", tags=["专案管理"])


@router.get("/", response_model=list[ProjectOut])
async def list_projects(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectConfig).order_by(ProjectConfig.display_order))
    return result.scalars().all()


@router.post("/", response_model=ProjectOut)
async def create_project(data: ProjectCreate, db: AsyncSession = Depends(get_db)):
    proj = ProjectConfig(**data.model_dump())
    db.add(proj)
    await db.commit()
    await db.refresh(proj)
    return proj


@router.patch("/{project_name}", response_model=ProjectOut)
async def update_project(project_name: str, data: ProjectUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectConfig).where(ProjectConfig.project_name == project_name))
    proj = result.scalars().first()
    if not proj:
        raise HTTPException(404, "专案不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(proj, k, v)
    await db.commit()
    await db.refresh(proj)
    return proj


@router.delete("/{project_name}")
async def delete_project(project_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectConfig).where(ProjectConfig.project_name == project_name))
    proj = result.scalars().first()
    if not proj:
        raise HTTPException(404, "专案不存在")
    await db.delete(proj)
    await db.commit()
    return {"ok": True}


# ── 重点站点 CRUD ──────────────────────────────────────────
@router.get("/{project_name}/key-stations", response_model=list[KeyStationOut])
async def list_key_stations(project_name: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProjectKeyStation)
        .where(ProjectKeyStation.project_name == project_name)
        .order_by(ProjectKeyStation.display_order)
    )
    return result.scalars().all()


@router.post("/{project_name}/key-stations", response_model=KeyStationOut)
async def create_key_station(project_name: str, data: KeyStationCreate, db: AsyncSession = Depends(get_db)):
    ks = ProjectKeyStation(project_name=project_name, **data.model_dump())
    db.add(ks)
    await db.commit()
    await db.refresh(ks)
    return ks


@router.patch("/{project_name}/key-stations/{ks_id}", response_model=KeyStationOut)
async def update_key_station(project_name: str, ks_id: int, data: KeyStationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectKeyStation).where(ProjectKeyStation.id == ks_id))
    ks = result.scalars().first()
    if not ks:
        raise HTTPException(404, "重点站点不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(ks, k, v)
    await db.commit()
    await db.refresh(ks)
    return ks


@router.delete("/{project_name}/key-stations/{ks_id}")
async def delete_key_station(project_name: str, ks_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ProjectKeyStation).where(ProjectKeyStation.id == ks_id))
    ks = result.scalars().first()
    if not ks:
        raise HTTPException(404, "重点站点不存在")
    await db.delete(ks)
    await db.commit()
    return {"ok": True}
