"""Token service module for JWT token generation and validation."""

from jose import jwt

from app.core.config import Settings

ALGORITHM = "HS256"


class NotRightTelegramData(Exception):
    pass


class TokensService:
    """Service for handling JWT token operations."""

    def __init__(self, config: Settings, safe_parse_webapp_init_data: callable):
        self.config = config
        self.safe_parse_webapp_init_data = safe_parse_webapp_init_data

    def verify(
        self,
        init_data: str,
    ) -> int:
        """Return user telegram id"""
        try:
            return self.safe_parse_webapp_init_data(
                init_data=init_data, token=self.config.BOT_TOKEN
            ).user.id
        except ValueError:
            raise NotRightTelegramData("Invalid authentication hash")

    def verify_access_token(self, token: str) -> int:
        if token.startswith("Bearer "):
            token = token[7:]
        try:
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=[ALGORITHM])
            return int(payload["sub"])
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
