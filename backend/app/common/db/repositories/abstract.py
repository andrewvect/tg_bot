"""Repository base file."""

from collections.abc import Sequence
from typing import Generic, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Base

AbstractModel = TypeVar("AbstractModel")


class Repository(Generic[AbstractModel]):
    type_model: type[Base]
    session: AsyncSession

    def __init__(self, type_model: type[Base], session: AsyncSession):
        self.type_model = type_model
        self.session = session

    async def get(self, identifier: int | str) -> AbstractModel:
        """Fetch a single entity by its identifier."""
        return await self.session.get(
            entity=self.type_model, ident=identifier, populate_existing=True
        )

    async def get_by_condition(self, condition) -> AbstractModel | None:
        """Fetch a single entity that meets a specific condition."""
        statement = select(self.type_model).where(condition)
        return (await self.session.execute(statement)).scalar()

    async def get_many(
        self, condition, limit: int = 100, order_by=None, options: list = None
    ) -> Sequence[Base]:
        """Fetch many entities that meet the condition, with optional sorting and limit."""
        statement = select(self.type_model).where(condition).limit(limit)
        if order_by:
            statement = statement.order_by(order_by)
        if options:
            statement = statement.options(*options)
        return (await self.session.scalars(statement)).unique().all()

    async def fetch_many(self, condition, limit: int = 100) -> Sequence[Base]:
        """Fetch many entities that meet the condition with a limit."""
        statement = select(self.type_model).where(condition).limit(limit)
        return (await self.session.scalars(statement)).unique().all()

    async def delete(self, condition) -> None:
        """Delete entities that meet the specified condition."""
        statement = delete(self.type_model).where(condition)
        await self.session.execute(statement)

    async def update(self, model) -> AbstractModel:
        """Update an entity"""
        model = await self.session.merge(model)
        await self.session.commit()
        return model
