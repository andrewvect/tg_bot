from app.common.db.models import Settings
from app.common.db.repositories import SettingsRepo
from app.schemas.settings import SettingsUpdateRequest


class SettingService:
    def __init__(self, repository: SettingsRepo):
        self.repository = repository

    async def get_user_settings(self, user_id: int) -> Settings:
        user = await self.repository.get_by_condition(
            condition=self.repository.type_model.user_id == user_id
        )

        if user is None:
            # Create default settings if not found
            user = Settings(user_id=user_id)
            # Use update instead of create
            user = await self.repository.update(user)

        return user

    async def update_user_settings(
        self, user_id: int, request: SettingsUpdateRequest
    ) -> Settings:
        user = await self.get_user_settings(user_id)
        if self._check_differece(user, request):
            user.spoiler_settings = request.spoiler_settings
            user.alphabet_settings = request.alphabet_settings
            user = await self.repository.update(user)
        return user

    def _check_differece(self, user: Settings, request: SettingsUpdateRequest) -> bool:
        return (
            user.spoiler_settings != request.spoiler_settings
            or user.alphabet_settings != request.alphabet_settings
        )
