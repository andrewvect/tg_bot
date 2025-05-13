from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from ...models.card import Card
from ..abstract import Repository

"""card_retriever.py

This module handles retrieving cards from the database.
"""

DEFAULT_LIMIT = 100


class NoCards(Exception):
    """Raised when there are no cards in the database"""

    pass


class CardRetriever(Repository[Card]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Card, session=session)

    async def get_many(
        self,
        filter_condition: Any,
        limit: int = DEFAULT_LIMIT,
        order_by: Any = None,
        options: list[Any] | None = None,
    ) -> list[Card]:
        """Retrieve multiple cards from the database based on a filter condition.

        Parameters:
        - filter_condition: SQLAlchemy clause to filter cards.
        - limit: Maximum number of cards to retrieve (default: 100).
        - order_by: Optional SQLAlchemy clause to order the result.
        - options: Optional list of load options.

        Returns:
        - List of Card objects.
        """
        result = await super().get_many(filter_condition, limit, order_by, options)
        if result is None:
            raise NoCards
        return list(result)
