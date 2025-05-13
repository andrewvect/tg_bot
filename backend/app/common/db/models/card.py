"""
Card model file.
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User  # noqa: F401
    from .word import Word  # noqa: F401
from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Card(Base):
    """
    Card model representing a user's interaction with specific words.
    """

    # Fields
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.telegram_id"), index=True
    )
    """Foreign key to User table, representing the user's telegram ID."""

    word_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("word.id"), index=True)
    """Word id"""

    count_of_views: Mapped[int] = mapped_column(Integer, nullable=False)
    """Count of how many times the card has been viewed"""

    last_view: Mapped[DateTime] = mapped_column(DateTime, nullable=False)
    """Timestamp of the last view"""

    # Constrains
    __table_args__ = (
        UniqueConstraint("user_id", "word_id", name="user_word_unique"),
        CheckConstraint(
            "count_of_views >= 0", name="check_count_of_views_non_negative"
        ),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="cards")  # noqa
    word: Mapped["Word"] = relationship("Word", back_populates="card")  # noqa

    def __str__(self) -> str:
        return f"Card for User ID {self.user_id} with Word ID {self.word_id} viewed {self.count_of_views} times"

    def __repr__(self) -> str:
        return f"<Card(user_id={self.user_id}, word_id={self.word_id}, count_of_views={self.count_of_views}, last_view={self.last_view})>"
