from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "MES 自动报表分析系统"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: str = "http://localhost:3000"

    # Database - MySQL
    DATABASE_URL: str = ""
    DATABASE_URL_SYNC: str = ""
    
    # Redis (optional)
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MES
    MES_BASE_URL: str = ""
    MES_LOGIN_PATH: str = "/Login.aspx"
    MES_USERNAME: str = ""
    MES_PASSWORD: str = ""
    MES_FACTORY: str = "Auto_THA"
    MES_DAY_SHIFT_START: str = "08:00"
    MES_DAY_SHIFT_END: str = "20:00"
    MES_NIGHT_SHIFT_START: str = "20:00"
    MES_NIGHT_SHIFT_END: str = "08:00"

    # Security
    SECRET_KEY: str = "dev_secret_key_change_in_production"
    AES_KEY: str = "dev_aes_key_32chars_change_prod!!"

    # Download path for Excel files
    DOWNLOAD_DIR: str = "/tmp/mes_downloads"

    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def MES_LOGIN_URL(self) -> str:
        return f"{self.MES_BASE_URL}{self.MES_LOGIN_PATH}"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# 确保下载目录存在
os.makedirs(settings.DOWNLOAD_DIR, exist_ok=True)
