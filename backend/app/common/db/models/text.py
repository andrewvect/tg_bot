from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Texts(Base):
    """Text model to store foreign and native texts for different language levels."""

    # Fields
    foreign_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    """ Title of the text in the foreign language """

    native_title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    """ Title of the text in the native language """

    foreign_text: Mapped[str] = mapped_column(Text, nullable=False)
    """ Full content of the text in the foreign language """

    native_text: Mapped[str] = mapped_column(Text, nullable=False)
    """ Full content of the text in the native language """

    level_id: Mapped[int] = mapped_column(ForeignKey("level.id"), nullable=False)
    """ Foreign key referencing the level of the text """

    # Relationships
    level: Mapped["Level"] = relationship("Level", lazy="joined")  # noqa
    """ Relationship with the Level model """

    user_texts: Mapped["UserText"] = relationship("UserText", back_populates="text")  # noqa
    """ Relationship with UserText model """

    def __str__(self):
        return f"{self.native_title} ({self.level})"

    def __repr__(self):
        return (
            f"<Texts(foreign_title={self.foreign_title}, native_title={self.native_title}, "
            f"level={self.level}, foreign_text={self.foreign_text}, native_text={self.native_text})>"
        )
