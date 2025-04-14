from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from ..models import Word
from .abstract import Repository

"""
word_repository.py

This module handles the repository functionality for managing `Word` entities.
"""


@dataclass
class WordData:
    native_word: str
    foreign_word: str
    image: str = None
    cyrillic_representation: str = None


class WordRepo(Repository[Word]):
    def __init__(self, session: AsyncSession) -> None:
        """
        Initialize the Word repository with a specific SQLAlchemy session.

        :param session: AsyncSession for database operations
        """
        super().__init__(type_model=Word, session=session)

    async def create(self, word_data: WordData) -> None:
        """
        Add a new word to the database using the provided WordData.

        :param word_data: Data required to create a new Word entity
        """
        word = self._create_word_entity(word_data)
        await self.session.merge(word)
        await self.session.commit()

    def _create_word_entity(self, word_data: WordData) -> Word:
        """
        Create and return a Word entity from the given WordData.

        This method encapsulates the creation logic and ensures separation of concerns.

        :param word_data: The data used to create a new Word entity
        :return: Word entity
        """
        return Word(
            native_word=word_data.native_word,
            foreign_word=word_data.foreign_word,
            image=word_data.image,
            cyrillic_word=word_data.cyrillic_representation,
        )

    async def get_new_words(self, last_word_id: int, limit: int = 5) -> list[Word]:
        """
        Get new words for the user with the given user_id,
        eagerly loading the related sentences to avoid n+1 problem.

        :param user_id: The ID of the user
        :param last_word_id: The ID of the last word retrieved
        :return: List of Word entities with sentences
        """
        query = await self.session.execute(
            select(Word)
            .options(joinedload(Word.sentences))
            .where(Word.id > last_word_id)
            .order_by(Word.id)
            .limit(limit)
        )
        return query.unique().scalars().all()
