"""
invoice_repository.py

This module contains the InvoiceRepository class for managing
invoice-related database operations such as creating and updating invoices.
"""

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Invoice
from .abstract import Repository

# Constants for avoiding magic strings
INVOICE_PREFIX = "INV-"
DEFAULT_STATUS = "pending"
DEFAULT_CURRENCY = "USD"


class InvoiceRepo(Repository[Invoice]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Invoice, session=session)

    async def create_invoice(
        self,
        user_id: int,
        invoice_id: str,
        price: float,
        payload: str,
        status: str = DEFAULT_STATUS,
        currency: str = DEFAULT_CURRENCY,
    ) -> Invoice:
        """Create a new invoice in the database."""
        try:
            new_invoice = self._create_invoice_object(
                user_id=user_id,
                invoice_id=invoice_id,
                status=status,
                currency=currency,
                price=price,
                payload=payload,
            )
            self.session.add(new_invoice)
            self.session.commit()
            return new_invoice
        except Exception as e:
            await self.session.rollback()
            logging.error(f"Failed to create invoice: {e}")
            raise

    async def update_status(self, invoice_id: str, status: str) -> Invoice:
        """Update the status of an existing invoice."""
        try:
            invoice = await self.get_by_condition(
                self.type_model.invoice_id == invoice_id
            )
            invoice.status = status
            await self.session.commit()
            return invoice
        except Exception as e:
            await self.session.rollback()
            logging.error(f"Failed to update invoice status: {e}")
            raise

    def _create_invoice_object(
        self,
        user_id: int,
        invoice_id: str,
        status: str,
        currency: str,
        price: float,
        payload: str,
    ) -> Invoice:
        """Encapsulate invoice creation logic to avoid bloating the main method."""
        return Invoice(
            user_id=user_id,
            invoice_id=invoice_id,
            status=status,
            currency=currency,
            price=price,
            payload=payload,
        )
