"""Word model file."""
from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .card import Card  # noqa: F401
    from .sentence import Sentence  # noqa: F401


class Word(Base):
    """Word model representing a word with translations, images, and related data."""

    # Fields

    # Frequency rank of the word (1 = most common), independent of the
    # primary key `id`. This is what lets a user pick a starting level
    # ("start from word 1000/2000/...") and what the import script assigns
    # from the source word lists, instead of overloading the PK for that.
    rank: Mapped[int] = mapped_column(
        Integer, unique=True, nullable=False, index=True
    )

    latin_word: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    """The foreign word (non-native language) Latin."""

    native_word: Mapped[str] = mapped_column(String(100), nullable=False)
    """The native word (translated version)."""

    cyrillic_word: Mapped[str] = mapped_column(String(100), nullable=True)
    """The Cyrillic word (translated version)."""

    image: Mapped[str | None] = mapped_column(String, nullable=True)
    """Optional image associated with the word."""

    legend: Mapped[str] = mapped_column(String, nullable=True)
    """Optional legend for the word."""

    transcription: Mapped[str | None] = mapped_column(String, nullable=True)
    """Optional transcription for the word."""

    voice_id: Mapped[str | None] = mapped_column(String, nullable=True)
    """Optional voice ID for the word pronunciation."""

    # Relationships
    sentences: Mapped[list["Sentence"] | None] = relationship(
        "Sentence", uselist=True, lazy="joined", cascade="all, delete"
    )
    """Related sentences using the word."""

    card: Mapped["Card"] = relationship(
        "Card", back_populates="word", cascade="all, delete"
    )
    """Related card that includes this word."""

    def __str__(self) -> str:
        return f"{self.latin_word} ({self.native_word})"

    def __repr__(self) -> str:
        return f"<Word(id={self.id}, foreign_word={self.latin_word}, native_word={self.native_word})>"
