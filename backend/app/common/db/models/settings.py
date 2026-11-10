from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User  # noqa: F401


class Settings(Base):
    """
    Settings model representing user-specific settings in the system.
    """

    alphabet_settings: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=3,
    )
    """ User's alphabet setting (use_two_alphabets=1, cyrilic_only=2, latin_only=3) """

    _alphabet_constraint = CheckConstraint(
        "alphabet_settings IN (1,2,3)", name="check_alphabet_settings"
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.telegram_id"),
        nullable=False,
        index=True,
        unique=True,
        doc="Foreign key to User's telegram_id",
    )
    """ Foreign key to User's telegram_id """

    spoiler_settings: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=1,
    )

    start_word_rank: Mapped[int] = mapped_column(
        sa.Integer,
        nullable=False,
        default=0,
    )
    """ Word frequency rank the user chose to start learning from (their
    "level"): 0 means the beginning, 1000/2000/... skips ahead. """

    # Constrains
    __table_args__ = (
        CheckConstraint(
            "spoiler_settings IN (0, 1, 2, 3, 4)", name="check_spoiler_settings"
        ),
        CheckConstraint(
            "start_word_rank >= 0", name="check_start_word_rank_non_negative"
        ),
    )
    """ Ensure spoiler_settings"""
    # Relationships
    user: Mapped["User"] = relationship(  # noqa
        "User",
        back_populates="settings",
        uselist=False,
        doc="Relationship to the associated User",
    )
    """ Relationship to the associated User """

    def __str__(self) -> str:
        return str(self.spoiler_settings)

    def __repr__(self) -> str:
        return f"<Settings(id={self.id}, spoiler_settings={self.spoiler_settings})>"
