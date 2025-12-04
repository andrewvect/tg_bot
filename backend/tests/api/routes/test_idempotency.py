"""Tests for idempotency middleware functionality."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_idempotency_middleware_installed(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    db_with_words,  # noqa: ARG001
    set_up_cache,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that idempotency middleware is installed and working."""
    idempotency_key = str(uuid.uuid4())

    # First request with idempotency key
    response1 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[0].id},
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response1.status_code == 201
    first_response_data = response1.json()

    # Second request with same idempotency key should return cached response
    response2 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[0].id},
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response2.status_code == 201
    second_response_data = response2.json()

    # Both responses should be identical
    assert first_response_data == second_response_data
    assert first_response_data["word_id"] == second_response_data["word_id"]
    assert first_response_data["user_id"] == second_response_data["user_id"]


@pytest.mark.asyncio
async def test_idempotency_different_keys_create_different_resources(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    db_with_words,  # noqa: ARG001
    set_up_cache,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that different idempotency keys create different resources."""
    idempotency_key1 = str(uuid.uuid4())
    idempotency_key2 = str(uuid.uuid4())

    # First request with first key
    response1 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[0].id},
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key1,
        },
    )

    assert response1.status_code == 201
    first_word_id = response1.json()["word_id"]

    # Second request with different key
    response2 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[1].id},
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key2,
        },
    )

    assert response2.status_code == 201
    second_word_id = response2.json()["word_id"]

    # Different keys should create different cards (different word_ids)
    assert first_word_id != second_word_id


@pytest.mark.asyncio
async def test_idempotency_without_key_creates_new_resources(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    db_with_words,  # noqa: ARG001
    set_up_cache,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that requests without idempotency key create new resources."""
    # First request without key
    response1 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[0].id},
        headers={
            "Authorization": "Bearer some_token",
        },
    )

    assert response1.status_code == 201
    first_word_id = response1.json()["word_id"]

    # Second request without key
    response2 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[1].id},
        headers={
            "Authorization": "Bearer some_token",
        },
    )

    assert response2.status_code == 201
    second_word_id = response2.json()["word_id"]

    # Without idempotency keys, different cards should be created (different word_ids)
    assert first_word_id != second_word_id


@pytest.mark.asyncio
async def test_idempotency_patch_request(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    db_with_cards,  # noqa: ARG001
    cache_with_created_cards,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test idempotency with PATCH requests."""
    idempotency_key = str(uuid.uuid4())

    request_data = {
        "passed": True,
        "word_id": db_with_cards[0].word_id,
    }

    # First PATCH request
    response1 = await client.patch(
        "/api/v1/cards/review/",
        json=request_data,
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response1.status_code == 201
    first_response_data = response1.json()

    # Second PATCH request with same idempotency key
    response2 = await client.patch(
        "/api/v1/cards/review/",
        json=request_data,
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response2.status_code == 201
    second_response_data = response2.json()

    # Responses should be identical
    assert first_response_data == second_response_data


@pytest.mark.asyncio
async def test_idempotency_get_request_not_cached(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    db_with_words,  # noqa: ARG001
    set_up_cache,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that GET requests are not affected by idempotency (they're safe operations)."""
    idempotency_key = str(uuid.uuid4())

    # First GET request
    response1 = await client.get(
        "/api/v1/cards/",
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response1.status_code == 200

    # Second GET request with same key
    response2 = await client.get(
        "/api/v1/cards/",
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response2.status_code == 200
    # GET requests should work normally regardless of idempotency key


@pytest.mark.asyncio
async def test_idempotency_key_format(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    db_with_words,  # noqa: ARG001
    set_up_cache,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that various idempotency key formats work correctly."""
    # Test with UUID format
    uuid_key = str(uuid.uuid4())
    response1 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[0].id},
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": uuid_key,
        },
    )
    assert response1.status_code == 201

    # Test with custom string format
    custom_key = "custom-idempotency-key-12345"
    response2 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[1].id},
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": custom_key,
        },
    )
    assert response2.status_code == 201

    # Verify caching works with custom key
    response3 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[1].id},
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": custom_key,
        },
    )
    assert response3.status_code == 201
    assert response2.json() == response3.json()


@pytest.mark.asyncio
async def test_idempotency_with_settings_put(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    test_user_settings,  # noqa: ARG001
    set_up_cache,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test idempotency with PUT requests for settings."""
    idempotency_key = str(uuid.uuid4())

    settings_data = {"spoiler_settings": 2, "alphabet_settings": 2}

    # First PUT request
    response1 = await client.put(
        "/api/v1/settings/",
        json=settings_data,
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response1.status_code == 200
    first_response_data = response1.json()

    # Second PUT request with same idempotency key
    response2 = await client.put(
        "/api/v1/settings/",
        json=settings_data,
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response2.status_code == 200
    second_response_data = response2.json()

    # Responses should be identical due to idempotency
    assert first_response_data == second_response_data
    assert first_response_data["spoiler_settings"] == 2


@pytest.mark.asyncio
async def test_idempotency_header_case_insensitive(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    db_with_words,  # noqa: ARG001
    set_up_cache,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that idempotency header is case-insensitive."""
    idempotency_key = str(uuid.uuid4())

    # Request with lowercase header
    response1 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[0].id},
        headers={
            "Authorization": "Bearer some_token",
            "idempotency-key": idempotency_key,
        },
    )

    assert response1.status_code == 201
    first_response_data = response1.json()

    # Request with mixed case header and same key
    response2 = await client.post(
        "/api/v1/cards/",
        json={"known": False, "word_id": db_with_words[0].id},
        headers={
            "Authorization": "Bearer some_token",
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response2.status_code == 201
    second_response_data = response2.json()

    # Should return the same cached response due to idempotency (case-insensitive headers)
    assert first_response_data == second_response_data
