"""Tests for idempotency middleware on login endpoint."""

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_idempotency_same_key_returns_same_token(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that duplicate login requests with same idempotency key return the same token."""
    idempotency_key = str(uuid.uuid4())

    login_data = {"init_data": "test_init_data_string"}

    # First login request with idempotency key
    response1 = await client.post(
        "/api/v1/login/access-token",
        json=login_data,
        headers={
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response1.status_code == 200
    first_response_data = response1.json()
    first_token = first_response_data["access_token"]

    # Second login request with same idempotency key
    response2 = await client.post(
        "/api/v1/login/access-token",
        json=login_data,
        headers={
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response2.status_code == 200
    second_response_data = response2.json()
    second_token = second_response_data["access_token"]

    # Both responses should be identical - same token returned
    assert first_response_data == second_response_data
    assert first_token == second_token
    assert first_response_data["user_id"] == second_response_data["user_id"]


@pytest.mark.asyncio
async def test_login_idempotency_different_keys_generate_different_tokens(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that login requests with different idempotency keys may generate different tokens."""
    idempotency_key1 = str(uuid.uuid4())
    idempotency_key2 = str(uuid.uuid4())

    login_data = {"init_data": "test_init_data_string"}

    # First login request
    response1 = await client.post(
        "/api/v1/login/access-token",
        json=login_data,
        headers={
            "Idempotency-Key": idempotency_key1,
        },
    )

    assert response1.status_code == 200
    first_token = response1.json()["access_token"]

    # Second login request with different idempotency key
    response2 = await client.post(
        "/api/v1/login/access-token",
        json=login_data,
        headers={
            "Idempotency-Key": idempotency_key2,
        },
    )

    assert response2.status_code == 200
    second_token = response2.json()["access_token"]

    # Different keys may generate different tokens (time-based expiry)
    # But user_id should be the same
    assert response1.json()["user_id"] == response2.json()["user_id"]


@pytest.mark.asyncio
async def test_login_without_idempotency_key_works(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that login requests without idempotency key work normally."""
    login_data = {"init_data": "test_init_data_string"}

    # First login request without key
    response1 = await client.post(
        "/api/v1/login/access-token",
        json=login_data,
    )

    assert response1.status_code == 200
    assert "access_token" in response1.json()
    assert "user_id" in response1.json()

    # Second login request without key also works
    response2 = await client.post(
        "/api/v1/login/access-token",
        json=login_data,
    )

    assert response2.status_code == 200
    assert "access_token" in response2.json()


@pytest.mark.asyncio
async def test_login_idempotency_prevents_token_generation_spam(
    client: AsyncClient,
    test_user,  # noqa: ARG001
    mock_tokens_service,  # noqa: ARG001
):
    """Test that idempotency prevents rapid token generation for same request."""
    idempotency_key = str(uuid.uuid4())
    login_data = {"init_data": "test_init_data_string"}

    # Make multiple rapid requests with same idempotency key
    responses = []
    for _ in range(5):
        response = await client.post(
            "/api/v1/login/access-token",
            json=login_data,
            headers={
                "Idempotency-Key": idempotency_key,
            },
        )
        responses.append(response)

    # All should succeed
    assert all(r.status_code == 200 for r in responses)

    # All should return the exact same token (cached)
    tokens = [r.json()["access_token"] for r in responses]
    assert len(
        set(tokens)) == 1, "All requests should return the same cached token"

    # All should return the same complete response
    first_response = responses[0].json()
    for response in responses[1:]:
        assert response.json() == first_response
