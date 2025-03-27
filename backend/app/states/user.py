from datetime import datetime, timedelta

from sortedcontainers import SortedDict, SortedList

from app.api.deps import get_session
from app.common.cache.states import UserProfile, users_states
from app.common.db import Database
from app.common.db.models.card import Card
from app.common.db.repositories.user import NoUsersFound


def review_algorithm(
    review_date: datetime, checks: int, passed: bool = True
) -> datetime:
    """Algorithm which define next review date"""
    # values which define how many minutes should pass before next review
    values = {
        1: 20,
        2: 40,
        3: 120,
        4: 240,
        5: 960,
        6: 3840,
        7: 15360,
        8: 61440,
        9: 245760,
        10: 983040,
    }
    if passed:
        if checks > 10:
            next_review = review_date + timedelta(minutes=values[10])
        else:
            next_review = review_date + timedelta(minutes=values[min(checks + 1, 10)])
    else:
        if checks < 3:
            next_review = review_date + timedelta(minutes=values[1])
        else:
            next_review = review_date + timedelta(minutes=values[checks - 3])

    return next_review


class StatesCreator:
    """Class create users states after app start and fill cache"""

    def __init__(self, db: Database, review_algorithm: callable, cache: dict):
        self.cache = cache
        self.db = db
        self.review_algorithm = review_algorithm

    async def create_states(self) -> dict[int, UserProfile]:
        try:
            users = await self.db.user.get_all_users()
        except NoUsersFound:
            return self.cache

        for user in users:
            telegram_id = user.telegram_id
            created_cards = await self.db.card.fetch_many(
                self.db.card.type_model.user_id == telegram_id
            )

            user_state = UserProfile(
                created_cards=self._fill_created_cards(created_cards),
                review_cards=self._fill_cards_to_review(created_cards),
                waiting_cards=self._fill_waiting_cards(created_cards),
            )

            self.cache[telegram_id] = user_state
        return self.cache

    def _fill_created_cards(self, cards: list[Card]) -> SortedList[int]:
        created_cards = SortedList()
        for card in cards:
            created_cards.add(card.id)
        return created_cards

    def _fill_cards_to_review(self, cards: list[Card]) -> list[int]:
        cards_to_review = []
        for card in cards:
            if (
                self.review_algorithm(card.last_view, card.count_of_views)
                < datetime.now()
            ):
                cards_to_review.append(card.id)
        return cards_to_review

    def _fill_waiting_cards(self, cards: list[Card]) -> SortedDict[int, int]:
        waiting_cards = SortedDict()
        for card in cards:
            review_date = self.review_algorithm(card.last_view, card.count_of_views)
            if review_date > datetime.now():
                waiting_cards[int(review_date.timestamp())] = card.id
        return waiting_cards

    def add_new_user(self, user_id: int):
        self.cache[user_id] = UserProfile(
            created_cards=SortedList(), review_cards=[], waiting_cards=SortedDict()
        )


async def build_user_state() -> StatesCreator:
    session = await anext(get_session())
    db = Database(session=session)
    states_creator = StatesCreator(db, review_algorithm, cache=users_states)
    return states_creator


async def get_users_states() -> dict[int, UserProfile]:
    """Return users states"""

    session = await anext(get_session())
    db = Database(session=session)
    states_creator = StatesCreator(db, review_algorithm, cache=users_states)
    return await states_creator.create_states()
