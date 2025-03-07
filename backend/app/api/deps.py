from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine

from app.core import security
from app.core.config import settings
from app.words import WordCardHandler
from app.common.cache import users_states

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


async def get_session() -> AsyncIterator[AsyncSession]:
    try:
        engine = create_async_engine(
            str(settings.ASYNC_SQLALCHEMY_DATABASE_URI),
            pool_size=20,
            max_overflow=10,
            pool_recycle=3600  # recycle connections after 1 hour
        )

        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False, future=True
        )
        session = async_session()
        yield session
    finally:
        await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


async def get_db(session: SessionDep) -> Database:
    return Database(session=session)

DbDep = Annotated[Database, Depends(get_db)]


def get_bot_instance() -> Bot:
    return Bot(token=settings.BOT_TOKEN)


BotDep = Annotated[Bot, Depends(get_bot_instance)]


def get_cache() -> dict:
    return users_states


CacheDep = Annotated[dict, Depends(get_cache)]


def get_word_card_handler(db: DbDep, cache: CacheDep) -> WordCardHandler:
    """Get an instance of WordCardHandler with database session and cache dependencies."""
    return WordCardHandler(db=db, cache=cache, review_algorithm=review_algorithm)


WordCardHandlerDep = Annotated[WordCardHandler, Depends(get_word_card_handler)]
