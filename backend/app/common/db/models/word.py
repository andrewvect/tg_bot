"""Word model file."""

from typing import List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .card import Card
from .sentence import Sentence


class Word(Base):
    """Word model representing a word with translations, images, and related data."""

    # Fields
    foreign_word: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    """The foreign word (non-native language)."""

    native_word: Mapped[str] = mapped_column(String(100), nullable=False)
    """The native word (translated version)."""

    image: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    """Optional image associated with the word."""

    legend: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    """Optional legend for the word."""

    transcription: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    """Optional transcription for the word."""

    voice_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    """Optional voice ID for the word pronunciation."""

    # Relationships
    sentences: Mapped[Optional[List["Sentence"]]] = relationship(
        "Sentence", uselist=True, lazy="joined", cascade="all, delete"
    )
    """Related sentences using the word."""

    card: Mapped["Card"] = relationship(
        "Card", back_populates="word", cascade="all, delete"
    )
    """Related card that includes this word."""

    def __str__(self):
        return f"{self.foreign_word} ({self.native_word})"

    def __repr__(self):
        return f"<Word(id={self.id}, foreign_word={self.foreign_word}, native_word={self.native_word})>"
