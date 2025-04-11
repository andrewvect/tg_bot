import pytest

from app.common.cache.states import users_states
from app.common.db.models import Card


@pytest.mark.asyncio
async def test_new_card_known_create(
    client,
    db_session,  # noqa
    test_user,  # noqa
    db_with_words,  # noqa
    set_up_cache,  # noqa
    mock_tokens_service,  # noqa
):
    """Test creating a new card with known word"""
    # Mock token service

    response = await client.post(
        "/api/v1/cards/",
        json={"known": True, "word_id": db_with_words[0].id},
        headers={"Authorization": "Bearer some_token"},
    )

    # check response
    # assert response.json() == 1
    assert response.status_code == 201
    # check db
    cards = db_session.query(Card).all()
    assert len(cards) == 1
    assert cards[0].user_id == test_user.telegram_id
    assert cards[0].count_of_views == 20

    # check cache
    assert len(users_states[test_user.telegram_id].created_cards) == 1
    assert len(users_states[test_user.telegram_id].known_cards) == 1

    assert len(users_states[test_user.telegram_id].review_cards) == 0
    assert len(users_states[test_user.telegram_id].waiting_cards) == 0

    assert users_states[test_user.telegram_id].known_cards[0] == cards[0].word_id
    assert users_states[test_user.telegram_id].created_cards[0] == cards[0].word_id

    # Clean up


@pytest.mark.asyncio
async def test_new_card_unknown_create(
    client,
    test_user,
    db_with_words,
    db_session,
    set_up_cache,  # noqa
    mock_tokens_service,  # noqa
):
    """Test creating a new card with known word"""

    response = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[0].id},
        headers={"Authorization": "Bearer some_token"},
    )

    # check response
    # assert response.json() == 1
    assert response.status_code == 201

    # check db
    cards = db_session.query(Card).all()
    assert len(cards) == 1
    assert cards[0].user_id == test_user.telegram_id
    assert cards[0].count_of_views == 1

    # check cache
    assert len(users_states[test_user.telegram_id].created_cards) == 1
    assert len(users_states[test_user.telegram_id].known_cards) == 0

    assert len(users_states[test_user.telegram_id].review_cards) == 1
    assert len(users_states[test_user.telegram_id].waiting_cards) == 0

    assert users_states[test_user.telegram_id].review_cards[0] == cards[0].word_id
    assert users_states[test_user.telegram_id].created_cards[0] == cards[0].word_id


@pytest.mark.asyncio
async def test_get_new_word(
    client,
    test_user,  # noqa
    db_with_words,  # noqa
    db_session,  # noqa
    set_up_cache,  # noqa
    mock_tokens_service,  # noqa
):
    """Test getting a new word"""

    response = await client.get(
        "api/v1/cards/", headers={"Authorization": "Bearer some_token"}
    )

    assert response.status_code == 200
    assert len(response.json()["words"]) == 10


@pytest.mark.asyncio
async def test_no_get_new_word(
    client,
    test_user,  # noqa
    db_session,  # noqa
    set_up_cache,  # noqa
    mock_tokens_service,  # noqa
):
    """Test getting a new word when there are no words in db"""

    response = await client.get(
        "api/v1/cards/", headers={"Authorization": "Bearer some_token"}
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "No more words in database"}


@pytest.mark.asyncio
async def test_add_success_review(
    client,
    test_user,
    db_with_cards,
    db_session,
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test adding a review"""

    response = await client.patch(
        "api/v1/cards/review/",
        json={"passed": True, "word_id": db_with_cards[0].word_id},
        headers={"Authorization": "Bearer some_token"},
    )

    # check response
    assert response.status_code == 201
    assert response.json() == {"message": "Review added successfully"}

    # check db
    card = db_session.query(Card).filter(Card.id == 1).first()
    db_session.refresh(card)  # Refresh session
    assert card.count_of_views == 2

    # check cache
    assert len(users_states[test_user.telegram_id].waiting_cards) == 1
    assert (
        len(users_states[test_user.telegram_id].review_cards) == len(db_with_cards) - 1
    )

    assert len(users_states[test_user.telegram_id].waiting_cards) == 1
    assert card.word_id in users_states[test_user.telegram_id].waiting_cards.values()


@pytest.mark.asyncio
async def test_add_fail_review(
    client,
    test_user,
    db_with_cards,
    db_session,
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test adding a fail review"""

    response = await client.patch(
        "api/v1/cards/review/",
        json={"passed": False, "word_id": db_with_cards[0].word_id},
        headers={"Authorization": "Bearer some_token"},
    )

    # check response
    assert response.status_code == 201
    assert response.json() == {"message": "Review added successfully"}

    # check db
    card = db_session.query(Card).filter(Card.id == 1).first()
    db_session.refresh(card)  # Refresh session
    assert card.count_of_views == 1

    # check cache
    assert len(users_states[test_user.telegram_id].waiting_cards) == 0
    assert len(users_states[test_user.telegram_id].review_cards) == len(db_with_cards)


@pytest.mark.asyncio
async def test_get_review_words(
    client,
    test_user,  # noqa
    db_with_cards,
    db_session,  # noqa
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test getting review words"""

    response = await client.get(
        "api/v1/cards/review/", headers={"Authorization": "Bearer some_token"}
    )

    assert response.status_code == 200
    assert len(response.json()["words"]) == len(db_with_cards)


@pytest.mark.asyncio
async def test_legend_field_in_response(
    client,
    test_user,  # noqa
    db_with_words,  # noqa
    db_session,  # noqa
    set_up_cache,  # noqa
    mock_tokens_service,  # noqa
):
    """Test legend field in new word"""

    response = await client.get(
        "api/v1/cards/", headers={"Authorization": "Bearer some_token"}
    )

    assert response.status_code == 200
    # check legend field
    assert response.json()["words"][0]["legend"] is not None
    assert response.json()["words"][0]["legend"] == db_with_words[0].legend
