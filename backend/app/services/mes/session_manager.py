"""
Session 保活管理器
每 30 分钟执行无操作请求，防止 MES Session 过期
"""
import asyncio
from playwright.async_api import Page
from app.services.mes.browser import get_page
from app.services.mes.login import login_to_mes, is_session_alive
from app.core.logging import setup_logging
from typing import Optional

logger = setup_logging()

_current_page: Optional[Page] = None
_page_lock = asyncio.Lock()


async def get_active_page() -> Page:
    """获取已登录的活跃页面，若 Session 失效则自动重登"""
    global _current_page

    async with _page_lock:
        if _current_page is None:
            _current_page = await get_page()
            await login_to_mes(_current_page)
            return _current_page

        alive = await is_session_alive(_current_page)
        if not alive:
            logger.warning("MES Session 已失效，正在重新登录...")
            await login_to_mes(_current_page)

        return _current_page


async def create_fresh_page() -> Page:
    """创建全新的已登录页面（用于并发采集）"""
    page = await get_page()
    await login_to_mes(page)
    return page


async def keepalive():
    """保活任务：定时触发，维持 Session"""
    try:
        page = await get_active_page()
        logger.debug("Session 保活检查通过")
    except Exception as e:
        logger.error(f"Session 保活失败: {e}")
