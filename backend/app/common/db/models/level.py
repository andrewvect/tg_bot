"""Level model file."""

from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Level(Base):
    """Texts levels model representing different levels with unique titles and validation."""

    # Fields
    level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    """Level integer, must be a positive value"""

    title: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    """Title of the level, unique and indexed"""

    __table_args__ = (CheckConstraint("level >= 0", name="check_level_positive"),)

    def __str__(self) -> str:
        return f"{self.title} ({self.level})"

    def __repr__(self) -> str:
        return f"<Level(level={self.level}, title={self.title})>"
