from app.common.db.models import Settings
from app.common.db.repositories import SettingsRepo
from app.schemas.settings import SettingsUpdateRequest  # if needed


class SettingService:
    def __init__(self, repository: SettingsRepo):
        self.repository = repository

    async def get_user_settings(self, user_id: int) -> Settings:
        user = await self.repository.get_by_condition(
            condition=self.repository.type_model.user_id == user_id
        )
        return user

    async def update_user_settings(
        self, user_id: int, request: SettingsUpdateRequest
    ) -> None:
        user = await self.get_user_settings(user_id)
        if self._check_differece(user, request):
            user.spoiler_settings = request.spoiler_settings
            user.alphabet_settings = request.alphabet_settings
            user = await self.repository.update(user)
        return user

    def _check_differece(self, user, request) -> bool:
        return (
            user.spoiler_settings != request.spoiler_settings
            or user.alphabet_settings != request.alphabet_settings
        )
