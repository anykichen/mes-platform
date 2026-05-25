"""
Playwright 浏览器管理
单例模式：整个进程共享一个 Browser 实例，减少启动开销
"""
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from app.core.config import settings
from app.core.logging import setup_logging
import asyncio
from typing import Optional

logger = setup_logging()

_playwright = None
_browser: Optional[Browser] = None
_context: Optional[BrowserContext] = None


async def get_browser() -> Browser:
    global _playwright, _browser
    if _browser is None or not _browser.is_connected():
        _playwright = await async_playwright().start()
        _browser = await _playwright.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-extensions",
            ],
        )
        logger.info("Playwright Chromium 已启动")
    return _browser


async def get_context() -> BrowserContext:
    global _context
    browser = await get_browser()
    if _context is None:
        _context = await browser.new_context(
            accept_downloads=True,
            viewport={"width": 1920, "height": 1080},
            locale="zh-CN",
        )
        logger.info("Browser context 已创建")
    return _context


async def get_page() -> Page:
    context = await get_context()
    page = await context.new_page()
    page.set_default_timeout(30000)  # 30秒超时
    return page


async def close_browser():
    global _browser, _context, _playwright
    if _context:
        await _context.close()
        _context = None
    if _browser:
        await _browser.close()
        _browser = None
    if _playwright:
        await _playwright.stop()
        _playwright = None
    logger.info("Playwright 已关闭")
