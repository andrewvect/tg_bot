"""statistics_repository.py

This module contains the repository for handling operations related to user statistics.
"""

from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Statistic
from .abstract import Repository


class StatisticsRepo(Repository[Statistic]):
    """
    Repository for handling Statistic operations.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the repository with the provided session.

        Args:
            session (AsyncSession): The database session to use.
        """
        super().__init__(type_model=Statistic, session=session)
        self._session = session

    async def add_statistic(self, user_id: int, stat_type: str) -> None:
        """
        Increment a specific statistic for the user.

        Args:
            user_id (int): The user's unique identifier.
            stat_type (str): The type of statistic to increment (e.g., 'create_card', 'known_card').
        """
        await self._update_daily_statistic(user_id=user_id, field_name=stat_type)

    async def initialize_statistic(self, user_id: int) -> None:
        """
        Initialize a Statistic entry for the user if it doesn't exist.

        Args:
            user_id (int): The user's unique identifier.
        """
        await self._session.merge(Statistic(user_id=user_id))
        await self._session.commit()

    async def _update_daily_statistic(self, user_id: int, field_name: str) -> None:
        """
        Update the statistic field for the user for the current day.

        Args:
            user_id (int): The user's unique identifier.
            field_name (str): The field of the statistic to update.
        """
        user_stats = await self._get_or_create_statistic(user_id)
        current_date = str(date.today())
        attr = getattr(user_stats, field_name)

        if current_date in attr:
            attr[current_date] += 1
        else:
            attr[current_date] = 1

        await self._session.commit()

    async def _get_or_create_statistic(self, user_id: int) -> Statistic:
        """
        Retrieve the user's statistic, or create a new one if it doesn't exist.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            Statistic: The user's statistic.
        """
        user_stats = await self.get_statistic(user_id)
        if user_stats is None:
            await self.initialize_statistic(user_id)
            user_stats = await self.get_statistic(user_id)

        return user_stats

    async def get_statistic(self, user_id: int) -> Statistic:
        """
        Get the Statistic for the given user.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            Statistic: The user's statistic.
        """
        result = await self.get_by_condition(
            condition=self.type_model.user_id == user_id
        )

        if result is None:
            await self.initialize_statistic(user_id)
            result = await self.get_by_condition(
                condition=self.type_model.user_id == user_id
            )

            # If we still don't have a result after initialization, create one directly
            if result is None:
                result = Statistic(user_id=user_id)
                self._session.add(result)
                await self._session.commit()
                # After adding and committing, we return the created object

        return result

    async def get_created_cards_today(self, user_id: int) -> int:
        """
        Get the number of cards created today by the user.

        Args:
            user_id (int): The user's unique identifier.

        Returns:
            int: The number of cards created today, or 0 if none found.
        """
        user_stats = await self.get_statistic(user_id)

        created_cards = user_stats.create_card
        current_date = str(date.today())

        return created_cards.get(current_date, 0)
