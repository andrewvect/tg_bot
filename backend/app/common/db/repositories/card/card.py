import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from src.backend.common.services.exceptions import NoCards

from ..models.card import Card
from .abstract import Repository


class CardRepo(Repository[Card]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Card, session=session)

    async def create(
        self, user_id: int, count_of_views: int, word_id: int, last_view=None
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

    async def get_many(self, whereclause, limit=100, order_by=None) -> list[Card]:
        """Get all cards from the database."""

        resutl = await super().get_many(whereclause, limit, order_by)
        if resutl is None:
            raise NoCards
        return resutl
