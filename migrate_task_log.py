"""
临时数据库迁移脚本：为 task_log 表添加缺失字段
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings


async def migrate():
    engine = create_async_engine(settings.DATABASE_URL)
    
    try:
        async with engine.begin() as conn:
            # 添加 success_count 字段
            try:
                await conn.run_sync(
                    lambda conn: conn.execute(
                        "ALTER TABLE task_log ADD COLUMN success_count INT NOT NULL DEFAULT 0"
                    )
                )
                print("✅ 添加 success_count 字段")
            except Exception as e:
                print(f"⚠️ success_count 可能已存在: {e}")
            
            # 添加 failed_count 字段
            try:
                await conn.run_sync(
                    lambda conn: conn.execute(
                        "ALTER TABLE task_log ADD COLUMN failed_count INT NOT NULL DEFAULT 0"
                    )
                )
                print("✅ 添加 failed_count 字段")
            except Exception as e:
                print(f"⚠️ failed_count 可能已存在: {e}")
            
            # 添加 error_message 字段
            try:
                await conn.run_sync(
                    lambda conn: conn.execute(
                        "ALTER TABLE task_log ADD COLUMN error_message TEXT NULL"
                    )
                )
                print("✅ 添加 error_message 字段")
            except Exception as e:
                print(f"⚠️ error_message 可能已存在: {e}")
        
        print("\n✅ 数据库迁移完成！")
    
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(migrate())
