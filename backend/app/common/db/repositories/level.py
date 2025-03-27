"""
level_repo.py

This module handles CRUD operations for the Level entity.
"""

import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Level
from .abstract import Repository


class LevelRepo(Repository[Level]):
    """Repository for managing Level entity CRUD operations and queries."""

    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Level, session=session)
        self.logger = logging.getLogger(__name__)

    async def create_level(self, level_title: str, stage_level: int) -> None:
        """Create a new level with the given title and stage level."""
        new_level = self._create_level_entity(level_title, stage_level)
        await self._add_and_commit(new_level)

    def _create_level_entity(self, level_title: str, stage_level: int) -> Level:
        """Factory method to create a new Level entity."""
        return self.type_model(title=level_title, level=stage_level)

    async def _add_and_commit(self, entity: Level) -> None:
        """Handles adding the entity and committing the transaction."""
        self.session.add(entity)
        try:
            await self.session.commit()
        except IntegrityError:
            await self.session.rollback()
            self.logger.info(f"Level with title {entity.title} already exists.")
