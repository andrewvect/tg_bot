from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .text import Texts  # noqa: F401
    from .user import User  # noqa: F401


class UserText(Base):
    """Relation many-to-many between users and texts."""

    # Fields
    user_telegram_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.telegram_id"), nullable=False, index=True
    )
    """The Telegram ID of the user. This field references the 'telegram_id' in the 'user' table.
    It is a required field (nullable=False) and indexed to improve query performance."""

    text_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("texts.id"), nullable=False, index=True
    )
    """The ID of the text. This field references the 'id' in the 'texts' table.
    It is a required field (nullable=False) and indexed for performance."""

    # Constraints
    __table_args__ = (
        UniqueConstraint("user_telegram_id", "text_id", name="user_text_unique"),
    )
    """A unique constraint that ensures the same user cannot be associated with the same text more than once.
    This constraint applies to the combination of 'user_telegram_id' and 'text_id'."""

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="texts")  # noqa
    """Relationship to the 'User' class.
    Establishes a bidirectional many-to-many relationship with users.
    The 'back_populates' argument connects it to the 'texts' attribute in the 'User' class."""

    text: Mapped["Texts"] = relationship("Texts", back_populates="user_texts")  # noqa
    """Relationship to the 'Texts' class.
    Establishes a bidirectional many-to-many relationship with texts.
    The 'back_populates' argument connects it to the 'user_texts' attribute in the 'Texts' class."""

    def __str__(self) -> str:
        return f"User: {self.user}, Text: {self.text}"

    def __repr__(self) -> str:
        return f"<UserText(user={self.user}, text={self.text})>"
