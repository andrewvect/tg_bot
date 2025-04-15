from collections.abc import AsyncGenerator
from typing import Annotated

from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from fastapi import Depends, HTTPException
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.common.cache import users_states
from app.common.db import Database
from app.common.db.repositories import SettingsRepo
from app.core.config import settings
from app.settings.service import SettingService
from app.token_service import TokensService
from app.utils.review_algoritm import review_algorithm
from app.words import WordCardHandler

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)

# Create engine once at module level
engine = create_async_engine(
    str(settings.ASYNC_SQLALCHEMY_DATABASE_URI),
    pool_size=10,
    max_overflow=20,
)

async_session_factory = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = async_session_factory()
    try:
        yield session
    finally:
        try:
            await session.close()
        except Exception:
            pass


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


def get_tokens_service() -> TokensService:
    return TokensService(
        config=settings, safe_parse_webapp_init_data=safe_parse_webapp_init_data
    )


TokensServiceDep = Annotated[TokensService, Depends(get_tokens_service)]


def get_settings_repo(session: SessionDep) -> SettingsRepo:
    return SettingsRepo(session=session)


SettingsRepoDep = Annotated[SettingsRepo, Depends(get_settings_repo)]


# New dependency for SettingService
def get_settings_service(
    settings_repo: SettingsRepo = Depends(get_settings_repo),
) -> SettingService:
    return SettingService(repository=settings_repo)


SettingsServiceDep = Annotated[SettingService, Depends(get_settings_service)]

# Set auto_error to True to enforce that the Authorization header is required
security_dep = HTTPBearer()


def verify_token(
    tokens_service: TokensServiceDep,
    token: Annotated[HTTPAuthorizationCredentials, Depends(security_dep)],
) -> int:
    """Verify the access token and return the user ID."""
    try:
        return tokens_service.verify_access_token(token.credentials)
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )
