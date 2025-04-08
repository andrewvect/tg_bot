import datetime
import logging
from collections.abc import AsyncGenerator, Generator
from unittest.mock import Mock, patch

import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.api.deps import get_session, get_tokens_service
from app.common.cache.states import UserProfile, users_states
from app.common.db.models import Base, Card, Settings, User, Word
from app.core.config import settings
from app.main import create_app

logger = logging.getLogger(__name__)
TEST_DB_NAME = "test_db"


@pytest.fixture(scope="session")
def override_settings():
    """Override application settings to use test database"""
    with patch.object(settings, "POSTGRES_DB", TEST_DB_NAME):
        yield


@pytest.fixture(scope="session")
def test_app(override_settings):  # noqa F811
    """Create a test instance of the app with patched settings"""
    return create_app()


@pytest.fixture(scope="session")
def engine(override_settings):  # noqa F811
    # Create a synchronous engine instead of async
    engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),  # Use the sync URI
        pool_pre_ping=True,
    )
    yield engine

    engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_engine(override_settings):  # noqa F811
    # Create an async engine
    async_engine = create_async_engine(
        str(settings.ASYNC_SQLALCHEMY_DATABASE_URI),
        echo=True,
        poolclass=NullPool,
    )
    yield async_engine

    await async_engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def clean_tables(engine):
    """Create and drop all tables for each test function."""
    with engine.begin() as conn:
        Base.metadata.drop_all(conn)
        Base.metadata.create_all(conn)
    yield


@pytest.fixture(scope="function")
def db_session_factory(engine):
    sync_session = sessionmaker(
        engine,
        class_=Session,
        expire_on_commit=False,
    )
    yield sync_session


@pytest.fixture(scope="session")
def async_db_session_factory(async_engine):
    async_session = sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield async_session


@pytest.fixture(scope="function")
def db_session(db_session_factory) -> Generator[Session, None, None]:
    session = db_session_factory()
    yield session
    session.close()
    logger.info("Closing DB session")


@pytest_asyncio.fixture(scope="function")
async def async_db_session(
    async_db_session_factory,
) -> Generator[AsyncSession, None, None]:
    session = async_db_session_factory()
    yield session
    await session.close()


@pytest.fixture(scope="function")
def test_user(db_session) -> User:
    user_data = {
        "telegram_id": 123456789,
        "user_name": "test_user",
        "first_name": "Test",
        "second_name": "User",
        "is_premium": False,
        "role": 0,
        "paid": False,
    }
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture(scope="function")
def test_user_settings(test_user, db_session):
    settings = Settings(user_id=test_user.telegram_id, spoiler_settings=1)
    db_session.add(settings)
    db_session.commit()
    return settings


@pytest.fixture(scope="function")
def db_with_words(request, db_session) -> list[Word]:
    count = 10  # default value
    if hasattr(request, "param"):
        if isinstance(request.param, dict):
            count = request.param.get("count", 10)
        else:
            count = request.param
    faker = Faker()
    ru_faker = Faker("ru_RU")
    words = []
    for _ in range(count):
        word = Word(
            foreign_word=faker.unique.word(),
            native_word=ru_faker.unique.word(),
            legend=faker.sentence(),
        )
        db_session.add(word)
        words.append(word)
    db_session.commit()
    return words


@pytest.fixture(scope="function")
def db_with_cards(db_session, test_user, db_with_words):
    cards = []
    for word in db_with_words:
        card = Card(
            user_id=test_user.telegram_id,
            word_id=word.id,
            count_of_views=1,
            last_view=datetime.datetime.now(),
        )
        db_session.add(card)
        cards.append(card)
    db_session.commit()
    return cards


@pytest.fixture(scope="function")
def set_up_cache(test_user):
    users_states[test_user.telegram_id] = UserProfile()


@pytest.fixture(scope="function")
def cache_with_created_cards(test_user, db_with_words, set_up_cache):  # noqa F811
    for word in db_with_words:
        users_states[test_user.telegram_id].created_cards.add(word.id)
        users_states[test_user.telegram_id].review_cards.append(word.id)
    yield users_states


@pytest.fixture(scope="function")
def mock_tokens_service(test_user, test_app, db_session):  # noqa F811
    def mock_token_service():
        mock = Mock()
        mock.verify_access_token.return_value = test_user.telegram_id
        mock.verify.return_value = test_user.telegram_id
        return mock

    test_app.dependency_overrides[get_tokens_service] = mock_token_service
    yield
    test_app.dependency_overrides = {}


@pytest.fixture(scope="function")
def override_app_session(test_app, async_db_session):
    test_app.dependency_overrides[get_session] = lambda: async_db_session
    yield
    test_app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="function")
async def client(test_app, override_app_session) -> AsyncGenerator[AsyncClient, None]:  # noqa F811
    """Provides an async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac
