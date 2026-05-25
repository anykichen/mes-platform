from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from app.core.config import settings


def _get_fernet() -> Fernet:
    """从 AES_KEY 派生 Fernet 密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"mes_platform_salt",
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(settings.AES_KEY.encode()))
    return Fernet(key)


def encrypt_password(plain: str) -> str:
    """加密 MES 密码，存入数据库"""
    f = _get_fernet()
    return f.encrypt(plain.encode()).decode()


def decrypt_password(encrypted: str) -> str:
    """解密 MES 密码"""
    f = _get_fernet()
    return f.decrypt(encrypted.encode()).decode()
