"""Structural interface (typing.Protocol) for the settings service.

See app/common/db/repositories/interfaces.py for the rationale: consumers
(WordCardHandler) should depend on this, not on the concrete SettingService.
"""

from typing import Protocol

from app.common.db.models import Settings
from app.schemas.settings import SettingsUpdateRequest


class SettingsServiceProtocol(Protocol):
    async def get_user_settings(self, user_id: int) -> Settings: ...

    async def update_user_settings(
        self, user_id: int, request: SettingsUpdateRequest
    ) -> Settings: ...
