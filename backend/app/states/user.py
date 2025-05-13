from collections.abc import Callable, Sequence
from datetime import datetime, timedelta

from sortedcontainers import SortedDict, SortedList  # type: ignore

from app.api.deps import async_session_factory
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

    def __init__(
        self,
        db: Database,
        review_func: Callable[[datetime, int, bool], datetime],
        cache: dict[int, UserProfile],
    ) -> None:
        self.cache = cache
        self.db = db
        self.review_algorithm = review_func

    async def create_states(self) -> dict[int, UserProfile]:
        try:
            users = await self.db.user.get_all_users()
        except NoUsersFound:
            return self.cache

        for user in users:
            telegram_id = user.telegram_id
            created_cards = await self.db.card.fetch_many(
                self.db.card.type_model.user_id == telegram_id, limit=10000
            )

            review_cards, waiting_cards = self._fill_review_waiting_cards(created_cards)

            user_state = UserProfile(
                created_cards=self._fill_created_cards(created_cards),
                review_cards=review_cards,
                waiting_cards=waiting_cards,
            )

            self.cache[telegram_id] = user_state
        return self.cache

    def _fill_created_cards(self, cards: Sequence[Card]) -> SortedList[int]:
        created_cards = SortedList()
        for card in cards:
            created_cards.add(card.word_id)
        return created_cards

    def _fill_review_waiting_cards(
        self, cards: Sequence[Card]
    ) -> tuple[list[int], SortedDict[int, int]]:
        cards_to_review = []
        waiting_cards = SortedDict()
        for card in cards:
            current_time = datetime.now()
            # Convert SQLAlchemy's DateTime to Python's datetime
            last_view_datetime = card.last_view
            if isinstance(last_view_datetime, datetime):
                review_date = self.review_algorithm(
                    last_view_datetime, card.count_of_views, True
                )
            else:
                # Handle the case where last_view might not be a datetime object
                continue

            if card.count_of_views == 20:
                pass
            elif review_date < current_time:
                cards_to_review.append(card.word_id)
            else:
                waiting_cards[int(review_date.timestamp())] = card.word_id

        return cards_to_review, waiting_cards

    def add_new_user(self, user_id: int) -> None:
        self.cache[user_id] = UserProfile(
            created_cards=SortedList(), review_cards=[], waiting_cards=SortedDict()
        )


async def build_user_state() -> StatesCreator:
    async with async_session_factory() as session:
        db = Database(session=session)
        states_creator = StatesCreator(db, review_algorithm, cache=users_states)
        return states_creator


async def get_users_states() -> dict[int, UserProfile]:
    """Return users states"""
    async with async_session_factory() as session:
        db = Database(session=session)
        states_creator = StatesCreator(db, review_algorithm, cache=users_states)
        return await states_creator.create_states()
