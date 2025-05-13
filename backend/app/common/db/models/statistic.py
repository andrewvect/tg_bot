from typing import TYPE_CHECKING

from sqlalchemy import JSON, ForeignKey
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Statistic(Base):
    """Model to store user statistics regarding card creation, review, and mastery."""

    # Fields
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.telegram_id"), index=True, nullable=False, unique=True
    )
    """ Foreign key referencing the User model's telegram_id """

    create_card: Mapped[dict[str, int]] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )
    """ Contains count of created cards by day """

    known_card: Mapped[dict[str, int]] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )
    """ Contains count of known cards by day """

    failed_review: Mapped[dict[str, int]] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )
    """ Contains count of failed reviews by day """

    success_review: Mapped[dict[str, int]] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )
    """ Contains count of successful reviews by day """

    master_card: Mapped[dict[str, int]] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )
    """ Contains count of mastered cards by day """

    readed_texts: Mapped[dict[str, int]] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict, nullable=False
    )
    """ Contains count of readed texts by day """

    # Relationships
    user = relationship("User", back_populates="statistic", lazy="joined")  # noqa
    """ Relationship to the User model """

    # Methods
    def __str__(self) -> str:
        return f"Statistic for user_id: {self.user_id}"

    def __repr__(self) -> str:
        return f"<Statistic(user_id={self.user_id}, created_cards={len(self.create_card)})>"
