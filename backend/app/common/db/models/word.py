"""Word model file."""


from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .card import Card
from .sentence import Sentence


class Word(Base):
    """Word model representing a word with translations, images, and related data."""

    # Fields
    latin_word: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    """The foreign word (non-native language) Latin."""

    native_word: Mapped[str] = mapped_column(String(100), nullable=False)
    """The native word (translated version)."""

    cyrillic_word: Mapped[str | None] = mapped_column(String(100), nullable=True)
    """The Cyrillic word (translated version)."""

    image: Mapped[str | None] = mapped_column(String, nullable=True)
    """Optional image associated with the word."""

    legend: Mapped[str | None] = mapped_column(String, nullable=True)
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

    def __str__(self):
        return f"{self.latin_word} ({self.native_word})"

    def __repr__(self):
        return f"<Word(id={self.id}, foreign_word={self.latin_word}, native_word={self.native_word})>"
