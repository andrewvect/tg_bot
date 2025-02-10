from app.core import db
import pytest
from sqlalchemy import select
from httpx import AsyncClient, ASGITransport

from app.api.routes.words import router
from app.common.shemas.words import NewCardRequest, ReviewRequest, WordResponse, WordsResponse
from app.common.db.models import Card
from app.common.cache.states import users_states
from app.api.deps import TokensServiceDep, get_tokens_service
from app.main import app


@pytest.mark.asyncio
async def test_new_card_known_create(client, test_user, db_with_words, db_session, set_up_cache, mock_tokens_service):
    """Test creating a new card with known word"""
    # Mock token service
    
    response = await client.post('/api/v1/cards/', cookies={"token": "test_token"}, json={"known": True})

    # check response
    assert response.status_code == 200
    assert response.json() == {"message": "Word card created successfully"}
    # check db
    card = await db_session.execute(select(Card))
    card = card.scalars().all()
    assert len(card) == 1
    assert card[0].user_id == test_user.telegram_id
    assert card[0].count_of_views == 20

    # check cache
    assert len(users_states[test_user.telegram_id].created_cards) == 1
    assert len(users_states[test_user.telegram_id].known_cards) == 1

    assert len(users_states[test_user.telegram_id].review_cards) == 0
    assert len(users_states[test_user.telegram_id].waiting_cards) == 0

    assert users_states[test_user.telegram_id].known_cards[0] == card[0].word_id
    assert users_states[test_user.telegram_id].created_cards[0] == card[0].word_id
@pytest.mark.asyncio
async def test_new_card_unknown_create(client, test_user, db_with_words, db_session, set_up_cache, mock_tokens_service):
    """Test creating a new card with known word"""

    response = await client.post('/api/v1/cards/', json={"known": False}, cookies={"token": "test_token"})

    # check response
    assert response.status_code == 200
    assert response.json() == {"message": "Word card created successfully"}
    # check db
    card = await db_session.execute(select(Card))
    card = card.scalars().all()
    assert len(card) == 1
    assert card[0].user_id == test_user.telegram_id
    assert card[0].count_of_views == 1

    # check cache
    assert len(users_states[test_user.telegram_id].created_cards) == 1
    assert len(users_states[test_user.telegram_id].known_cards) == 0

    assert len(users_states[test_user.telegram_id].review_cards) == 1
    assert len(users_states[test_user.telegram_id].waiting_cards) == 0

    assert users_states[test_user.telegram_id].review_cards[0] == card[0].word_id
    assert users_states[test_user.telegram_id].created_cards[0] == card[0].word_id


@pytest.mark.asyncio
async def test_get_new_word(client, test_user,  db_with_words, db_session, set_up_cache, mock_tokens_service):
    """Test getting a new word"""

    response = await client.get('api/v1/cards/', cookies={"token": "test_token"})
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        response = await ac.get('api/v1/cards/', cookies={"token": "test_token"})

    assert response.status_code == 200
    assert len(response.json()['words']) == 5


@pytest.mark.asyncio
async def test_no_get_new_word(client, test_user,  db_session, set_up_cache, mock_tokens_service):
    """Test getting a new word when there are no words in db"""

    response = await client.get('api/v1/cards/', cookies={"token": "test_token"})

    assert response.status_code == 400
    assert response.json() == {"detail": "No more words in database"}


@pytest.mark.asyncio
async def test_add_success_review(client, test_user, db_with_cards, db_session, cache_with_created_cards, mock_tokens_service):
    """Test adding a review"""

    response = await client.post('api/v1/cards/review/', json={"passed": True}, cookies={"token": "test_token"})

    # check response
    assert response.status_code == 200
    assert response.json() == {"message": "Review added successfully"}

    # check db
    result = await db_session.execute(select(Card).where(Card.id == 1))
    card = result.scalar()
    await db_session.refresh(card)  # Refresh session
    assert card.count_of_views == 2

    # check cache
    assert len(users_states[test_user.telegram_id].waiting_cards) == 1
    assert len(users_states[test_user.telegram_id].review_cards) == len(
        db_with_cards) - 1

    assert len(users_states[test_user.telegram_id].waiting_cards) == 1
    assert card.word_id in users_states[test_user.telegram_id].waiting_cards.values(
    )


