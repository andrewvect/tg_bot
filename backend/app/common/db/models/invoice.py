"""Invoice model file."""

import datetime

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Invoice(Base):
    """Invoice model representing payment invoices."""

    __tablename__ = "invoice"

    # Fields
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.telegram_id"), nullable=False
    )
    """Foreign key to User table, representing the user's telegram ID."""

    invoice_id: Mapped[str] = mapped_column(
        String(255), nullable=False, primary_key=True
    )
    """Unique identifier for the invoice."""

    status: Mapped[str] = mapped_column(String(50), nullable=False)
    """Invoice status, such as 'paid', 'pending', 'failed'."""

    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    """Currency code for the invoice, e.g., 'USD', 'EUR'. Default is nullable."""

    price: Mapped[float] = mapped_column(Float, nullable=True)
    """Price of the invoice in the specified currency."""

    payload: Mapped[str] = mapped_column(String, nullable=True)
    """Optional payload attached to the invoice."""

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, default=func.now()
    )
    """Timestamp for when the invoice was created."""

    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=True, onupdate=func.now()
    )
    """Timestamp for when the invoice was last updated."""

    # Constraints
    __table_args__ = (
        CheckConstraint("price >= 0", name="check_price_positive"),
        Index("idx_invoice_user_id", "user_id"),
        Index("idx_invoice_status", "status"),
    )

    # Relationships
    user = relationship("User", back_populates="invoices", lazy="joined")
    """Relationship to the User table, representing the user who owns the invoice."""

    def __str__(self):
        return (
            f"Invoice(invoice_id={self.invoice_id}, user_id={self.user_id}, status={self.status}, "
            f"currency={self.currency}, price={self.price}, payload={self.payload}, "
            f"created_at={self.created_at}, updated_at={self.updated_at})"
        )

    def __repr__(self):
        return f"<Invoice(invoice_id={self.invoice_id}, user_id={self.user_id}, status={self.status}, price={self.price})>"
