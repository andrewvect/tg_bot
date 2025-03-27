from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..models import UserText
from .abstract import Repository


class UserTextRepo(Repository[UserText]):
    """Repository for UserText model."""

    def __init__(self, session: AsyncSession):
        super().__init__(type_model=UserText, session=session)
        self._session = session

    async def create(self, user_id: int, text_id: int) -> UserText:
        """
        Creates a new UserText entry

        Args:
            user_id (int): The ID of the user creating the text entry.
            text_id (int): The ID of the text being referenced.

        Returns:
            UserText: The newly created UserText object.
        """
        user_text_entry = UserText(user_telegram_id=user_id, text_id=text_id)
        self.session.add(user_text_entry)
        await self.session.commit()
        return user_text_entry

    async def get_subquery_by_user_id(self, user_id: int) -> UserText:
        """Return subquery with user relations with texts."""
        subquery = select(UserText.text_id).filter(UserText.user_telegram_id == user_id)
        return subquery
