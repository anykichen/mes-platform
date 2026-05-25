import sys
from loguru import logger
from app.core.config import settings


def setup_logging():
    logger.remove()
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    logger.add(
        "logs/mes_platform.log",
        level="DEBUG",
        rotation="00:00",       # 每天午夜滚动
        retention="30 days",    # 保留30天
        compression="zip",
        encoding="utf-8",
    )
    return logger
