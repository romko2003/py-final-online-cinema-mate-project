import re

from passlib.context import CryptContext

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Мінімум 8 символів, 1 літера, 1 цифра
_PASSWORD_RE = re.compile(r"^(?=.*[A-Za-z])(?=.*\d).{8,}$")


class PasswordManager:
    @staticmethod
    def validate(password: str) -> None:
        if not _PASSWORD_RE.match(password):
            raise ValueError("Password must be 8+ chars and contain letters and digits.")

    @staticmethod
    def hash(password: str) -> str:
        return _pwd_context.hash(password)

    @staticmethod
    def verify(password: str, hashed: str) -> bool:
        return _pwd_context.verify(password, hashed)
