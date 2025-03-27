"""User model file."""

from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm.properties import MappedColumn

from .base import Base


class User(Base):
    """User model."""

    # Fields
    telegram_id: Mapped[int] = mapped_column(
        sa.BigInteger, unique=True, nullable=False, index=True, primary_key=True
    )
    """ Telegram user id """

    user_name: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    """ Telegram user name """

    first_name: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    """ Telegram profile first name """

    second_name: Mapped[str] = mapped_column(sa.Text, unique=False, nullable=True)
    """ Telegram profile second name """

    is_premium: Mapped[bool] = mapped_column(
        sa.Boolean, unique=False, nullable=False, default=False
    )
    """ Premium status in telegram """

    date_registration: Mapped[datetime] = mapped_column(
        sa.DateTime, nullable=False, default=sa.func.now()
    )
    """ Date of registration """

    role: MappedColumn[int] = mapped_column(sa.Integer, nullable=False, default=0)
    """ Role of the user """

    paid: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    """ Whether the user has paid or not """

    # Relationships
    cards: Mapped[list["Card"] | None] = relationship(  # noqa
        "Card", back_populates="user", lazy="joined"
    )
    """ Relationship with Card model """

    settings: Mapped["Settings"] = relationship(  # noqa
        "Settings", back_populates="user", uselist=False, lazy="joined"
    )
    """ Relationship with Settings model """

    texts: Mapped[list["UserText"] | None] = relationship(  # noqa
        "UserText", back_populates="user", lazy="joined"
    )
    """ Relationship with UserText model """

    invoices: Mapped[list["Invoice"] | None] = relationship(  # noqa
        "Invoice", back_populates="user", lazy="joined"
    )
    """ Relationship with Invoice model """

    statistic: Mapped[list["Statistic"] | None] = relationship(  # noqa
        "Statistic", back_populates="user", lazy="joined"
    )
    """ Relationship with Statistic model """

    def __str__(self):
        return f"{self.first_name} {self.second_name} ({self.user_name})"

    def __repr__(self):
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, user_name={self.user_name})>"
