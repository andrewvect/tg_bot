"""
sentence_repository.py

This module defines the repository for handling CRUD operations
and SQL queries related to Sentence.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Sentence
from .abstract import Repository


class SentenceRepo(Repository[Sentence]):
    """Repository for handling CRUD and SQL queries related to Sentence."""

    def __init__(self, session: AsyncSession):
        """
        Initialize SentenceRepo with the provided async session.

        Args:
            session (AsyncSession): The database session for executing queries.
        """
        super().__init__(type_model=Sentence, session=session)
        self._session: AsyncSession = session  # Encapsulate session to make it private.

    async def create(self, sentence: str, translation: str, word_id: int) -> None:
        """
        Create a new Sentence entry in the database.

        Args:
            sentence (str): The sentence text.
            translation (str): The translation of the sentence.
            word_id (int): The ID of the related word.
        """
        new_sentence: Sentence = self._build_sentence(sentence, translation, word_id)
        await self._save_sentence(new_sentence)

    def _build_sentence(
        self, sentence: str, translation: str, word_id: int
    ) -> Sentence:
        """
        Helper method to build a Sentence object.

        Args:
            sentence (str): The sentence text.
            translation (str): The translation of the sentence.
            word_id (int): The ID of the related word.

        Returns:
            Sentence: The constructed Sentence object.
        """
        return Sentence(sentence=sentence, translation=translation, word_id=word_id)

    async def _save_sentence(self, sentence: Sentence) -> None:
        """
        Save the sentence to the database using merge.

        Args:
            sentence (Sentence): The sentence object to be saved.
        """
        logging.info(f"Saving sentence: {sentence.sentence}")
        await self._session.merge(sentence)
