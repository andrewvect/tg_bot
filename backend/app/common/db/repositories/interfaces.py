"""Structural interfaces (typing.Protocol) for repositories.

GRASP Protected Variations / Indirection: a consumer (a service, a handler,
the Database facade's own attribute annotations) should depend on what a
collaborator does, not on which concrete class implements it - so a fake or
alternate implementation can stand in without ever touching the consumer.

Protocols are structural (PEP 544): every existing Repository subclass
already satisfies the matching protocol below purely by having compatible
methods, with no explicit inheritance or other change needed.
"""

import datetime
from collections.abc import Sequence
from typing import Any, Protocol, TypeVar

from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.expression import UnaryExpression

from app.common.db.models import Card, Settings, User, Word
from app.common.db.repositories.abstract import WhereClause

ModelT = TypeVar("ModelT")


class RepositoryProtocol(Protocol[ModelT]):
    """What every repository exposes, independent of which model it wraps."""

    type_model: type[ModelT]

    async def get(self, identifier: int | str) -> ModelT | None: ...

    async def get_by_condition(self, condition: WhereClause) -> ModelT | None: ...

    async def get_many(
        self,
        condition: WhereClause,
        limit: int = 100,
        order_by: UnaryExpression[Any] | ColumnElement[Any] | None = None,
        options: list[Any] | None = None,
    ) -> Sequence[ModelT]: ...

    async def fetch_many(
        self, condition: WhereClause, limit: int = 100
    ) -> Sequence[ModelT]: ...

    async def delete(self, condition: WhereClause) -> None: ...

    async def update(self, model: ModelT) -> ModelT: ...


class WordRepoProtocol(RepositoryProtocol[Word], Protocol):
    """Adds what WordCardHandler needs beyond the generic repository surface."""

    async def get_new_words(self, min_rank: int, limit: int = 5) -> list[Word]: ...


class CardRepoProtocol(RepositoryProtocol[Card], Protocol):
    """Adds what WordCardHandler needs beyond the generic repository surface."""

    async def create_card(
        self,
        user_id: int,
        count_of_views: int,
        word_id: int,
        last_view: datetime.datetime | None = None,
    ) -> Card: ...

    async def add_review(self, user_id: int, word_id: int) -> Card: ...


class SettingsRepoProtocol(RepositoryProtocol[Settings], Protocol):
    """Adds what bot command handlers need beyond the generic repository surface."""

    async def create_or_update_settings(
        self, user_id: int, spoiler_value: int = 1
    ) -> None: ...


class UserRepoProtocol(RepositoryProtocol[User], Protocol):
    """Adds what StatesCreator needs beyond the generic repository surface."""

    async def get_all_users(self) -> list[User]: ...
