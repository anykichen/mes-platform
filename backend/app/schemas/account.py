from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AccountUpdate(BaseModel):
    username: str
    password: str  # 明文，后端加密存储


class AccountOut(BaseModel):
    id: int
    username: str
    last_login_at: Optional[datetime]
    last_login_ok: Optional[bool]
    updated_at: datetime
    model_config = {"from_attributes": True}


class LoginTestResult(BaseModel):
    success: bool
    message: str
    tested_at: datetime
