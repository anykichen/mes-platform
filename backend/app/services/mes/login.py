"""
MES 登录服务
- 自动登录 / 重登
- 密码错误检测
- Session 状态检查
"""
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from app.core.config import settings
from app.core.security import decrypt_password
from app.core.logging import setup_logging
from app.db.session import AsyncSessionLocal
from app.models.account import MesAccount
from sqlalchemy import select
from datetime import datetime

logger = setup_logging()


class LoginError(Exception):
    pass


class PasswordExpiredError(Exception):
    pass


async def get_mes_credentials() -> tuple[str, str]:
    """从数据库读取 MES 账号密码（解密）"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(MesAccount).limit(1))
        account = result.scalars().first()
        if not account:
            raise LoginError("未配置 MES 账号，请在系统设置中添加")
        return account.username, decrypt_password(account.password_encrypted)


@retry(
    retry=retry_if_exception_type(LoginError),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)
async def login_to_mes(page: Page) -> bool:
    """
    登录 MES 系统
    返回 True = 登录成功
    抛出 PasswordExpiredError = 密码已过期
    抛出 LoginError = 登录失败
    """
    username, password = await get_mes_credentials()

    try:
        logger.info(f"正在登录 MES: {settings.MES_LOGIN_URL}")
        await page.goto(settings.MES_LOGIN_URL, wait_until="networkidle")

        # 填写账号密码
        await page.fill('input[name="username"], #username, input[type="text"]', username)
        await page.fill('input[name="password"], #password, input[type="password"]', password)
        await page.click('input[type="submit"], button[type="submit"], #btnLogin')

        # 等待页面跳转
        await page.wait_for_load_state("networkidle", timeout=15000)
        current_url = page.url

        # 检测密码过期页面
        if "ChangePassword" in current_url or "change_password" in current_url.lower():
            raise PasswordExpiredError("MES 密码已过期，请在系统设置中更新密码")

        # 检测登录失败（仍在登录页）
        if "Login" in current_url or "login" in current_url.lower():
            error_text = await page.text_content(".error-msg, .alert-danger, #lblMessage") or ""
            raise LoginError(f"MES 登录失败: {error_text.strip() or '账号或密码错误'}")

        # 更新数据库登录状态
        await _update_login_status(success=True)
        logger.info("MES 登录成功")
        return True

    except (PasswordExpiredError, LoginError):
        await _update_login_status(success=False)
        raise
    except PlaywrightTimeout as e:
        await _update_login_status(success=False)
        raise LoginError(f"MES 登录超时: {e}")
    except Exception as e:
        await _update_login_status(success=False)
        raise LoginError(f"MES 登录异常: {e}")


async def is_session_alive(page: Page) -> bool:
    """检查当前 Session 是否有效"""
    try:
        await page.goto(f"{settings.MES_BASE_URL}/Production/KPI", wait_until="networkidle", timeout=10000)
        if "Login" in page.url:
            return False
        return True
    except Exception:
        return False


async def _update_login_status(success: bool):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(MesAccount).limit(1))
        account = result.scalars().first()
        if account:
            account.last_login_at = datetime.utcnow()
            account.last_login_ok = success
            await db.commit()
