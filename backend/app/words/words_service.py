import datetime

from app.common.cache.states import UserProfile
from app.common.db.database import Database
from app.common.db.models import Word
from app.common.db.models.card import Card
from app.common.shemas.words import WordResponse


class EndWordsInDb(Exception):
    """No more words in the database"""

    pass


class EndWordsToReview(Exception):
    """No more words to review"""

    pass


class WordCardHandler:
    def __init__(
        self, db: Database, cache: dict[int, UserProfile], review_algorithm: callable
    ):
        self.db = db
        self.cache = cache
        self.review_algorithm: callable = review_algorithm

    async def create_new_card(
        self, telegram_id: int, known: bool, word_id: int
    ) -> Card:
        """Create a new word card for user"""

        if word_id in self.cache[telegram_id].created_cards:
            raise ValueError("Word card already created")

        if word_id != 1 and len(self.cache[telegram_id].created_cards) == 0:
            if word_id != self.cache[telegram_id].created_cards[-1] + 1:
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

    async def get_new_words(self, user_id: int, limit: int = 5) -> list[Word]:
        """Get new words for user"""

        if len(self.cache[user_id].created_cards) == 0:
            lats_word_id = 0
        else:
            lats_word_id = self.cache[user_id].created_cards[-1]

        words = await self.db.word.get_new_words(limit=limit, last_word_id=lats_word_id)
        if not words:
            raise EndWordsInDb("No more words in database")
        return words

    async def add_review(self, user_id: int, passed: bool, word_id: int) -> None:
        """Add review for word"""

        self.cache[user_id].review_cards.remove(word_id)

        if passed:
            card = await self.db.card.add_review(user_id=user_id, word_id=word_id)
            self.cache[user_id].waiting_cards[
                self.review_algorithm(checks=card.count_of_views)
            ] = word_id

        else:
            self.cache[user_id].review_cards.append(word_id)

    async def get_review_words(
        self, user_id: int, limit: int = 20
    ) -> list[WordResponse]:
        """Get words for review"""

        self._refresh_user_reviews(user_id)

        if len(self.cache[user_id].review_cards) < limit:
            limit = len(self.cache[user_id].review_cards)

        review_words_ids = self.cache[user_id].review_cards[0:limit]

        words = await self.db.word.get_many(condition=Word.id.in_(review_words_ids))

        if not words:
            raise EndWordsToReview("No words to review")
        return words

    def get_review_words_count(self, user_id: int) -> int:
        """Get count of words for review"""
        self._refresh_user_reviews(user_id)

        return len(self.cache[user_id].review_cards)

    def _refresh_user_reviews(self, user_id):
        current_time = int(datetime.datetime.now().timestamp())
        for date_review, word_id in self.cache[user_id].waiting_cards.items():
            if date_review < current_time:
                self.cache[user_id].review_cards.append(word_id)
                del self.cache[user_id].waiting_cards[date_review]
            else:
                break
