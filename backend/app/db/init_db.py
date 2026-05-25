"""
数据库初始化：建表 + 创建月分区 + 插入种子数据
运行: python -m app.db.init_db
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.db.base import Base
from app.models import project, station, account, task_log  # noqa: F401 触发模型注册


async def init():
    engine = create_async_engine(settings.DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表已创建")

    # 插入默认种子数据
    from app.db.session import AsyncSessionLocal
    from app.models.project import ProjectConfig
    from app.models.account import MesAccount
    from app.core.security import encrypt_password
    from sqlalchemy import select

    async with AsyncSessionLocal() as db:
        # 默认专案
        result = await db.execute(select(ProjectConfig))
        if not result.scalars().first():
            defaults = [
                ProjectConfig(project_name="Project A", enabled=True, display_order=1),
                ProjectConfig(project_name="Project B", enabled=True, display_order=2),
                ProjectConfig(project_name="Project C", enabled=False, display_order=3),
            ]
            db.add_all(defaults)

        # 默认 MES 账号
        acc = await db.execute(select(MesAccount))
        if not acc.scalars().first():
            db.add(MesAccount(
                username=settings.MES_USERNAME or "mes_user",
                password_encrypted=encrypt_password(settings.MES_PASSWORD or "password"),
            ))

        await db.commit()
        print("✅ 种子数据已写入")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init())
