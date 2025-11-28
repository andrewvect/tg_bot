import uuid

import pytest
from sqlalchemy.orm.session import Session

from app.common.cache.states import idempotency_store, users_states
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
        len(users_states[test_user.telegram_id].review_cards) == len(
            db_with_cards) - 1
    )

    assert len(users_states[test_user.telegram_id].waiting_cards) == 1
    assert card.word_id in users_states[test_user.telegram_id].waiting_cards.values(
    )


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
    assert len(users_states[test_user.telegram_id].review_cards) == len(
        db_with_cards)


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


@pytest.mark.asyncio
async def test_return_sentences(
    client,
    test_user,  # noqa
    db_with_words,  # noqa
    db_with_sentences,  # noqa
    db_session: Session,  # noqa
    set_up_cache,  # noqa
    mock_tokens_service,  # noqa
):
    """Test return sentences for word"""

    response = await client.get(
        "api/v1/cards/",
        headers={"Authorization": "Bearer some_token"},
    )

    assert response.status_code == 200
    sentences = response.json()["words"][0]["sentences"]
    # For each sentence, check that after removing an optional 'id' key,
    # exactly 3 objects are present.
    expected_keys = {"id", "cyrilic_text", "latin_text", "native_text"}
    for sentence in sentences:
        assert set(sentence.keys()) == expected_keys


@pytest.mark.asyncio
async def test_return_sentences_with_review_words(
    client,
    test_user,  # noqa
    db_with_words,  # noqa
    db_with_sentences,  # noqa
    db_session: Session,  # noqa
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test return sentences for word"""

    response = await client.get(
        "api/v1/cards/review/",
        headers={"Authorization": "Bearer some_token"},
    )

    assert response.status_code == 200
    sentences = response.json()["words"][0]["sentences"]
    expected_keys = {"id", "cyrilic_text", "latin_text", "native_text"}
    for sentence in sentences:
        assert set(sentence.keys()) == expected_keys


# Idempotency Tests


@pytest.mark.asyncio
async def test_review_idempotency_same_key_returns_cached_response(
    client,
    test_user,
    db_with_cards,
    db_session,
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test that using the same idempotency key returns cached response without processing review again"""
    idempotency_key = str(uuid.uuid4())

    # First request
    response1 = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": True,
            "word_id": db_with_cards[0].word_id,
            "idempotency_key": idempotency_key,
        },
        headers={"Authorization": "Bearer some_token"},
    )

    assert response1.status_code == 201
    assert response1.json() == {"message": "Review added successfully"}

    # Check DB state after first request
    card_after_first = db_session.query(Card).filter(
        Card.id == db_with_cards[0].id).first()
    db_session.refresh(card_after_first)
    first_count_of_views = card_after_first.count_of_views
    first_waiting_cards_count = len(
        users_states[test_user.telegram_id].waiting_cards)

    # Second request with same idempotency key
    response2 = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": True,
            "word_id": db_with_cards[0].word_id,
            "idempotency_key": idempotency_key,
        },
        headers={"Authorization": "Bearer some_token"},
    )

    # Should return same response
    assert response2.status_code == 201
    assert response2.json() == {"message": "Review added successfully"}

    # Check that DB was NOT modified again
    card_after_second = db_session.query(Card).filter(
        Card.id == db_with_cards[0].id).first()
    db_session.refresh(card_after_second)
    assert card_after_second.count_of_views == first_count_of_views
    assert len(
        users_states[test_user.telegram_id].waiting_cards) == first_waiting_cards_count


@pytest.mark.asyncio
async def test_review_idempotency_different_keys_process_separately(
    client,
    test_user,
    db_with_cards,
    db_session,
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test that different idempotency keys result in separate review processing"""
    idempotency_key1 = str(uuid.uuid4())
    idempotency_key2 = str(uuid.uuid4())

    # First request with first key
    response1 = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": True,
            "word_id": db_with_cards[0].word_id,
            "idempotency_key": idempotency_key1,
        },
        headers={"Authorization": "Bearer some_token"},
    )

    assert response1.status_code == 201

    # Second request with different key (should fail because word already reviewed)
    response2 = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": True,
            "word_id": db_with_cards[1].word_id,
            "idempotency_key": idempotency_key2,
        },
        headers={"Authorization": "Bearer some_token"},
    )

    assert response2.status_code == 201
    # Both reviews should be processed independently
    assert response1.json() == response2.json()


@pytest.mark.asyncio
async def test_review_idempotency_user_scoped(
    client,
    test_user,
    db_with_cards,
    db_session,
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test that idempotency keys are scoped per user"""
    idempotency_key = str(uuid.uuid4())

    # Store a fake response for different user with same key
    fake_user_id = 99999
    idempotency_store.store(
        idempotency_key,
        fake_user_id,
        {"message": "Different user's response"}
    )

    # Request with test_user should not get fake user's cached response
    response = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": True,
            "word_id": db_with_cards[0].word_id,
            "idempotency_key": idempotency_key,
        },
        headers={"Authorization": "Bearer some_token"},
    )

    assert response.status_code == 201
    assert response.json() == {"message": "Review added successfully"}
    # Not the fake response
    assert response.json() != {"message": "Different user's response"}


@pytest.mark.asyncio
async def test_review_idempotency_store_cleanup(
    client,
    test_user,
    db_with_cards,
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test that idempotency store can be cleared"""
    idempotency_key = str(uuid.uuid4())

    # First request
    response1 = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": True,
            "word_id": db_with_cards[0].word_id,
            "idempotency_key": idempotency_key,
        },
        headers={"Authorization": "Bearer some_token"},
    )

    assert response1.status_code == 201

    # Verify key is stored
    cached = idempotency_store.check(idempotency_key, test_user.telegram_id)
    assert cached is not None

    # Clear store
    idempotency_store.clear()

    # Verify key is gone
    cached_after_clear = idempotency_store.check(
        idempotency_key, test_user.telegram_id)
    assert cached_after_clear is None


@pytest.mark.asyncio
async def test_review_missing_idempotency_key(
    client,
    test_user,
    db_with_cards,
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test that missing idempotency_key in request returns validation error"""
    response = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": True,
            "word_id": db_with_cards[0].word_id,
            # Missing idempotency_key
        },
        headers={"Authorization": "Bearer some_token"},
    )

    # Should return 422 validation error
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_review_idempotency_failed_review(
    client,
    test_user,
    db_with_cards,
    db_session,
    cache_with_created_cards,  # noqa
    mock_tokens_service,  # noqa
):
    """Test idempotency works with failed reviews (passed=False)"""
    idempotency_key = str(uuid.uuid4())

    # First failed review request
    response1 = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": False,
            "word_id": db_with_cards[0].word_id,
            "idempotency_key": idempotency_key,
        },
        headers={"Authorization": "Bearer some_token"},
    )

    assert response1.status_code == 201
    assert response1.json() == {"message": "Review added successfully"}

    # Check cache state
    review_cards_count_after_first = len(
        users_states[test_user.telegram_id].review_cards)

    # Second request with same key
    response2 = await client.patch(
        "api/v1/cards/review/",
        json={
            "passed": False,
            "word_id": db_with_cards[0].word_id,
            "idempotency_key": idempotency_key,
        },
        headers={"Authorization": "Bearer some_token"},
    )

    assert response2.status_code == 201
    assert response2.json() == {"message": "Review added successfully"}

    # Verify cache wasn't modified again
    review_cards_count_after_second = len(
        users_states[test_user.telegram_id].review_cards)
    assert review_cards_count_after_second == review_cards_count_after_first
