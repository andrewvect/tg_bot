import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Settings
from .abstract import Repository


class SettingsRepo(Repository[Settings]):
    """
    Settings Repository handles the creation and updating of user settings.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Settings, session=session)
        self.logger = logging.getLogger(__name__)

    async def create_or_update_settings(
        self, user_id: int, spoiler_value: int = 1
    ) -> None:
        """
        Creates or updates the settings for a specific user.

        :param user_id: The ID of the user whose settings are being updated.
        :param spoiler_value: The new value for the user's spoiler settings.
        """
        await self._merge_settings(user_id, spoiler_value)
        await self._commit_session()

    async def _merge_settings(self, user_id: int, spoiler_value: int) -> None:
        """
        Merges new or updated settings into the session.

        :param user_id: The ID of the user whose settings are being merged.
        :param spoiler_value: The value to set for the user's spoiler settings.
        """
        await self.session.merge(
            Settings(user_id=user_id, spoiler_settings=spoiler_value)
        )

    async def _commit_session(self) -> None:
        """Commits the current session to save any changes."""
        try:
            await self.session.commit()
        except IntegrityError:
            self.logger.error("User settings already exist")
            await self.session.rollback()
