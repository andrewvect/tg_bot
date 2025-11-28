import datetime
import logging
from collections.abc import AsyncGenerator, Generator
from typing import Any
from unittest.mock import Mock

import pytest
import pytest_asyncio
from faker import Faker
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from app.api.deps import get_session, get_tokens_service
from app.common.cache.states import UserProfile, users_states
from app.common.db.models import Base, Card, Sentence, Settings, User, Word
from app.core.config import settings
from app.main import create_app

logger = logging.getLogger(__name__)
TEST_DB_NAME = "test_db"


@pytest.fixture(scope="session")
def test_app():
    """Create a test instance of the app"""
    return create_app()


@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    """Create the test database using SQLAlchemy."""

    from sqlalchemy.engine.url import make_url

    url = make_url(str(settings.SQLALCHEMY_DATABASE_URI))
    url = url.set(database="postgres")
    engine = create_engine(url, pool_pre_ping=True)

    # Create a connection to the default database
    from sqlalchemy.sql import text

    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        # Drop the test database if it exists
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))
        # Create the test database
        conn.execute(text(f"CREATE DATABASE {TEST_DB_NAME}"))

    yield

    # Cleanup: Drop the test database after tests
    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(text(f"DROP DATABASE IF EXISTS {TEST_DB_NAME}"))


@pytest.fixture(scope="session")
def engine() -> Generator[Engine, None, None]:
    # Create a synchronous engine instead of async
    engine = create_engine(
        str(settings.SQLALCHEMY_DATABASE_URI),  # Use the sync URI
        pool_pre_ping=True,
    )
    yield engine

    engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def async_engine() -> AsyncGenerator[AsyncEngine, None]:
    # Create an async engine
    async_engine = create_async_engine(
        str(settings.ASYNC_SQLALCHEMY_DATABASE_URI),
        echo=True,
        poolclass=NullPool,
    )
    yield async_engine

    await async_engine.dispose()


@pytest.fixture(scope="function", autouse=True)
def clean_tables(engine: Engine) -> Generator[None, None, None]:
    """Create and drop all tables for each test function."""
    with engine.begin() as conn:
        Base.metadata.drop_all(conn)
        Base.metadata.create_all(conn)
    yield


@pytest.fixture(scope="function")
def db_session_factory(engine: Engine) -> Generator[sessionmaker[Session], None, None]:
    sync_session = sessionmaker(
        engine,
        class_=Session,
        expire_on_commit=False,
    )
    yield sync_session


@pytest.fixture(scope="session")
def async_db_session_factory(async_engine: AsyncEngine) -> Generator[Any, None, None]:
    async_session = async_sessionmaker(
        async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    yield async_session


@pytest.fixture(scope="function")
def db_session(db_session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    session = db_session_factory()
    yield session
    session.close()
    logger.info("Closing DB session")


@pytest_asyncio.fixture(scope="function")
async def async_db_session(
    async_db_session_factory: Any,
) -> AsyncGenerator[AsyncSession, None]:
    session = async_db_session_factory()
    yield session
    await session.close()


@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    user_data: dict[str, Any] = {
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
def test_user_settings(test_user: User, db_session: Session) -> Settings:
    settings = Settings(user_id=test_user.telegram_id, spoiler_settings=1)
    db_session.add(settings)
    db_session.commit()
    return settings


@pytest.fixture(scope="function")
def db_with_words(request: pytest.FixtureRequest, db_session: Session) -> list[Word]:
    count: int = 10  # default value
    if hasattr(request, "param"):
        if isinstance(request.param, dict):
            count = request.param.get("count", 10)  # type: ignore[assignment]
        else:
            count = request.param  # type: ignore[assignment]
    faker = Faker()
    ru_faker = Faker("ru_RU")
    words = []
    for _ in range(count):
        word = Word(
            latin_word=faker.unique.word(),
            native_word=ru_faker.unique.word(),
            legend=faker.sentence(),
            cyrillic_word=ru_faker.unique.word(),
        )
        db_session.add(word)
        words.append(word)
    db_session.commit()
    return words


@pytest.fixture(scope="function")
def db_with_cards(db_session: Session, test_user: User, db_with_words: list[Word]) -> list[Card]:
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
def db_with_sentences(
    db_session: Session,  # noqa F811
    test_user: User,  # noqa F811
    db_with_words: list[Word],  # noqa F811
) -> list[Sentence]:
    sentences = []
    fake = Faker()
    for word in db_with_words:
        for _ in range(3):
            sentence_obj = Sentence(
                native_text=fake.unique.sentence(),
                cyrilic_text=fake.unique.sentence(),
                latin_text=fake.unique.sentence(),
                word_id=word.id,
            )
            db_session.add(sentence_obj)
            sentences.append(sentence_obj)
    db_session.commit()
    return sentences


@pytest.fixture(scope="function")
def set_up_cache(test_user: User) -> None:
    users_states[test_user.telegram_id] = UserProfile()


@pytest.fixture(scope="function")
def cache_with_created_cards(test_user: User, db_with_words: list[Word], set_up_cache: None) -> Generator[Any, None, None]:  # noqa F811
    for word in db_with_words:
        users_states[test_user.telegram_id].created_cards.add(word.id)
        users_states[test_user.telegram_id].review_cards.append(word.id)
    yield users_states


@pytest.fixture(scope="function")
def mock_tokens_service(test_user: User, test_app: Any, db_session: Session) -> Generator[None, None, None]:  # noqa F811
    def mock_token_service() -> Mock:
        mock = Mock()
        mock.verify_access_token.return_value = test_user.telegram_id
        mock.verify.return_value = test_user.telegram_id
        return mock

    test_app.dependency_overrides[get_tokens_service] = mock_token_service
    yield
    test_app.dependency_overrides = {}


@pytest.fixture(scope="function")
def override_app_session(test_app: Any, async_db_session: AsyncSession) -> Generator[None, None, None]:
    test_app.dependency_overrides[get_session] = lambda: async_db_session
    yield
    test_app.dependency_overrides = {}


@pytest_asyncio.fixture(scope="function")
async def client(test_app: Any, override_app_session: None) -> AsyncGenerator[AsyncClient, None]:  # noqa F811
    """Provides an async HTTP client for testing FastAPI endpoints."""
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as ac:
        yield ac
