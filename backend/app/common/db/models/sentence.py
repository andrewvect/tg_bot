from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Sentence(Base):
    """Sentence model"""

    # Fields
    native_text: Mapped[str] = mapped_column(
        String(length=255), nullable=False, index=True
    )
    """ Native sentence text """

    foreign_text: Mapped[str] = mapped_column(String(length=255), nullable=False)
    """ Foreign sentence text """

    word_id: Mapped[int] = mapped_column(
        ForeignKey("word.id"), nullable=False, index=True
    )
    """ Foreign key to the Word model """

    # Relationships
    word_bk: Mapped["Word"] = relationship(  # noqa
        "Word", back_populates="sentences", uselist=False
    )
    """ Relationship to the Word model """

    def __str__(self):
        return f"{self.native_text} - {self.foreign_text}"

    def __repr__(self):
        return f"<Sentence(id={self.id}, native_text={self.native_text}, foreign_text={self.foreign_text})>"
