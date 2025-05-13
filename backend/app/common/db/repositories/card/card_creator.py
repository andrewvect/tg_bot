"""
card_creator.py

This module handles the creation of user cards and insertion into the database.
"""

import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ...models.card import Card
from ..abstract import Repository


class NoCards(Exception):
    """Raised when there are no cards in the database"""

    pass


class CardRepo(Repository[Card]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Card, session=session)

    async def create_card(
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

    async def add_review(self, user_id: int, word_id: int) -> Card:
        """Add a review for a word."""
        result = await self.session.execute(
            select(Card).filter(Card.user_id == user_id, Card.word_id == word_id)
        )
        card = result.scalars().first()
        if card is None:
            raise NoCards("No card found for the specified user and word")
        card.count_of_views += 1
        await self.session.commit()
        return card
