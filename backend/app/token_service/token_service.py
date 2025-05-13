"""Token service module for JWT token generation and validation."""
from collections.abc import Callable
from typing import Any

from jose import jwt  # type: ignore

from app.core.config import Settings

ALGORITHM = "HS256"


class NotRightTelegramData(Exception):
    pass


class TokensService:
    """Service for handling JWT token operations."""

    def __init__(
        self, config: Settings, safe_parse_webapp_init_data: Callable[..., Any]
    ):
        self.config = config
        self.safe_parse_webapp_init_data = safe_parse_webapp_init_data

    def verify(
        self,
        init_data: str,
    ) -> int:
        """Return user telegram id"""
        try:
            user_data = self.safe_parse_webapp_init_data(
                init_data=init_data, token=self.config.BOT_TOKEN
            )
            # Explicitly cast the user ID to int to avoid returning Any
            return int(user_data.user.id)
        except ValueError:
            raise NotRightTelegramData("Invalid authentication hash")

    def verify_access_token(self, token: str) -> int:
        try:
            payload = jwt.decode(token, self.config.SECRET_KEY, algorithms=[ALGORITHM])
            if "sub" not in payload:
                raise ValueError("Invalid token: missing subject")
            user_id = int(payload["sub"])
            return user_id
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
