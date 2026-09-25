import datetime
from collections.abc import Callable

from sqlalchemy.orm import joinedload

from app.common.cache.states import UserProfile
from app.common.db.database import Database
from app.common.db.models import Word
from app.common.db.models.card import Card
from app.settings.service import SettingService


class EndWordsInDb(Exception):
    """No more words in the database"""

    pass


class EndWordsToReview(Exception):
    """No more words to review"""

    pass


class WordCardHandler:
    def __init__(
        self,
        db: Database,
        cache: dict[int, UserProfile],
        review_algorithm: Callable[
            [int, bool, datetime.datetime | None], datetime.datetime
        ],
        settings_service: SettingService,
    ):
        self.db = db
        self.cache = cache
        self.review_algorithm = review_algorithm
        self.settings_service = settings_service

    async def _get_min_rank(self, user_id: int) -> int:
        """Lowest rank the user has already unlocked.

        This is the higher of: the rank of the last word they created a
        card for, and their chosen starting level (Settings.start_word_rank)
        - so picking a level jumps them ahead, but never rewinds progress
        they've already made past it.
        """
        user_settings = await self.settings_service.get_user_settings(user_id)
        starting_rank = user_settings.start_word_rank

        if len(self.cache[user_id].created_cards) == 0:
            return starting_rank

        latest_word = await self.db.word.get(self.cache[user_id].created_cards[-1])
        latest_rank = latest_word.rank if latest_word else 0
        return max(latest_rank, starting_rank)

    async def create_new_card(
        self, telegram_id: int, known: bool, word_id: int
    ) -> Card:
        """Create a new word card for user"""

        if word_id in self.cache[telegram_id].created_cards:
            raise ValueError("Word card already created")

        word = await self.db.word.get(word_id)
        if word is None:
            raise ValueError("Word not found")

        min_rank = await self._get_min_rank(telegram_id)
        if word.rank != min_rank + 1:
            raise ValueError("Word card not in sequence")

        if known is True:
            count_of_views = 20
            self.cache[telegram_id].known_cards.add(word_id)
        else:
            count_of_views = 1
            self.cache[telegram_id].review_cards.append(word_id)

        created_card = await self.db.card.create_card(
            word_id=word_id,
            user_id=telegram_id,
            count_of_views=count_of_views,
        )

        self.cache[telegram_id].created_cards.add(word_id)

        return created_card

    async def get_new_words(self, user_id: int, limit: int = 20) -> list[Word]:
        """Get new words for user"""

        min_rank = await self._get_min_rank(user_id)

        words = await self.db.word.get_new_words(limit=limit, min_rank=min_rank)
        if not words:
            raise EndWordsInDb("No more words in database")
        return words

    async def add_review(self, user_id: int, passed: bool, word_id: int) -> None:
        """Add review for word"""

        self.cache[user_id].review_cards.remove(word_id)

        if passed:
            card = await self.db.card.add_review(user_id=user_id, word_id=word_id)
            self.cache[user_id].waiting_cards[
                self.review_algorithm(card.count_of_views, False, None)
            ] = word_id

        else:
            self.cache[user_id].review_cards.append(word_id)

    async def get_review_words(self, user_id: int, limit: int = 20) -> list[Word]:
        """Get words for review"""

        self._refresh_user_reviews(user_id)

        if len(self.cache[user_id].review_cards) < limit:
            limit = len(self.cache[user_id].review_cards)

        review_words_ids = self.cache[user_id].review_cards[0:limit]

        words = await self.db.word.get_many(
            condition=Word.id.in_(review_words_ids),
            options=[joinedload(Word.sentences)],
        )

        if not words:
            raise EndWordsToReview("No words to review")
        return list(words)

    def get_review_words_count(self, user_id: int) -> int:
        """Get count of words for review"""
        self._refresh_user_reviews(user_id)

        return len(self.cache[user_id].review_cards)

    def _refresh_user_reviews(self, user_id: int) -> None:
        current_time = int(datetime.datetime.now().timestamp())
        for date_review, word_id in self.cache[user_id].waiting_cards.items():
            if date_review < current_time:
                self.cache[user_id].review_cards.append(word_id)
                del self.cache[user_id].waiting_cards[date_review]
            else:
                break
