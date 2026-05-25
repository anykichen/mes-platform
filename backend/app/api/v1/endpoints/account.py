from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from app.db.session import get_db
from app.models.account import MesAccount
from app.schemas.account import AccountUpdate, AccountOut, LoginTestResult
from app.core.security import encrypt_password
from app.services.mes.browser import get_page
from app.services.mes.login import login_to_mes

router = APIRouter(prefix="/account", tags=["MES账号"])


@router.get("/", response_model=AccountOut)
async def get_account(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MesAccount).limit(1))
    acc = result.scalars().first()
    if not acc:
        raise HTTPException(404, "未配置 MES 账号")
    return acc


@router.put("/", response_model=AccountOut)
async def update_account(data: AccountUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(MesAccount).limit(1))
    acc = result.scalars().first()
    if acc:
        acc.username = data.username
        acc.password_encrypted = encrypt_password(data.password)
    else:
        acc = MesAccount(
            username=data.username,
            password_encrypted=encrypt_password(data.password),
        )
        db.add(acc)
    await db.commit()
    await db.refresh(acc)
    return acc


@router.post("/test-login", response_model=LoginTestResult)
async def test_login():
    """测试 MES 登录是否成功"""
    try:
        page = await get_page()
        await login_to_mes(page)
        await page.close()
        return LoginTestResult(success=True, message="登录成功", tested_at=datetime.utcnow())
    except Exception as e:
        return LoginTestResult(success=False, message=str(e), tested_at=datetime.utcnow())
