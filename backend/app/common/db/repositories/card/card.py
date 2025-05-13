import datetime
from collections.abc import Sequence
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.common.db.repositories.card.card_creator import NoCards

from ...models.card import Card
from ..abstract import Repository


class CardRepo(Repository[Card]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Card, session=session)

    async def create(
        self,
        user_id: int,
        count_of_views: int,
        word_id: int,
        last_view: datetime.datetime | None = None,
    ) -> Card:
        """Insert a new user card into the database."""
        if last_view is None:
            last_view = datetime.datetime.now()
        card = Card(
            user_id=user_id,
            count_of_views=count_of_views,
            word_id=word_id,
            last_view=last_view,
        )
        self.session.add(card)
        await self.session.commit()
        return card

    async def get_many(
        self,
        condition: Any,
        limit: int = 100,
        order_by: Any = None,
        options: list[Any] | None = None,
    ) -> Sequence[Card]:
        """Get all cards from the database."""
        result = await super().get_many(condition, limit, order_by, options)
        if result is None:
            raise NoCards
        return result
