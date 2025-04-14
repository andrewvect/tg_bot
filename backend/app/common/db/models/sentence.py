from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Sentence(Base):
    """Sentence model"""

    # Fields
    native_text: Mapped[str] = mapped_column(Text, nullable=False)
    """ Native sentence text """

    cyrilic_text: Mapped[str] = mapped_column(Text, nullable=False)
    """ Cyrillic sentence text """

    latin_text: Mapped[str] = mapped_column(Text, nullable=False)
    """ Latin sentence text """

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
        return (
            f"{self.native_text} "
            f"- "
            f"{self.cyrilic_text} "
            f"- "
            f"{self.latin_text}"
        )

    def __repr__(self):
        return (
            f"<Sentence("
            f"id={self.id}, "
            f"native_text={self.native_text}, "
            f"cyrilic_text={self.cyrilic_text}, "
            f"latin_text={self.latin_text}, "
            f"word_id={self.word_id}"
            f")>"
        )
