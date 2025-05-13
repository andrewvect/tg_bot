"""
texts_repo.py

This module contains the repository class for fetching Texts entities from the database.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Texts
from .abstract import Repository

MIN_LEVEL = 0


class TextNotFound(Exception):
    """Raised when no text is found in the database"""

    pass


class TextsRepo(Repository[Texts]):
    def __init__(self, session: AsyncSession):
        """
        Initializes the TextsRepo with a session.

        Parameters:
            session (AsyncSession): The async session used for database queries.
        """
        super().__init__(type_model=Texts, session=session)

    async def get_random_text_by_level(self, level: int) -> Texts:
        """
        Fetches a random text matching the specified level.

        Parameters:
            level (int): The level of the text to fetch.

        Returns:
            Texts: A random text object that matches the level or None if no result is found.
        """

        query = (
            select(self.type_model)
            .filter(self.type_model.level_id == level)
            .order_by(func.random())
        )
        result = await self.session.execute(query)
        text = result.scalars().first()

        if text is None:
            raise TextNotFound

        return text

    async def get_random_text_by_no_marked_user(
        self, subquery: list[int], level: int
    ) -> Texts:
        """Fetches a random text matching the specified level and not marked by user.

        Parameters:
            subquery (list[int]): List of user_id
            level (int): The level of the text to fetch.

        Returns:
            Texts: A random text object that matches the level or None if no result is found.
        """

        query = (
            select(self.type_model)
            .where(self.type_model.level_id == level)
            .where(~self.type_model.id.in_(subquery))
            .order_by(func.random())
        )

        result = await self.session.execute(query)

        text = result.scalars().first()

        if text is None:
            raise TextNotFound

        return text
