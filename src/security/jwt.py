from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

ALGORITHM = "HS256"


class JWTManager:
    def __init__(self, secret_key: str) -> None:
        self.secret_key = secret_key

    def encode(self, payload: dict[str, Any], ttl: timedelta) -> str:
        now = datetime.now(timezone.utc)
        to_encode = payload | {"iat": int(now.timestamp()), "exp": int((now + ttl).timestamp())}
        return jwt.encode(to_encode, self.secret_key, algorithm=ALGORITHM)

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(token, self.secret_key, algorithms=[ALGORITHM])
