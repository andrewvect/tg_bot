"""Tests for idempotency middleware on webhook endpoint."""

import uuid
from typing import Any

import pytest
from httpx import AsyncClient

from app.api.deps import get_bot_instance


@pytest.mark.asyncio
async def test_webhook_idempotency_prevents_duplicate_processing(
    client: AsyncClient,
    test_app: Any,
    mock_bot: Any,
):
    """Test that duplicate webhook events with same idempotency key are processed only once."""
    # Override the Bot dependency with our mock
    test_app.dependency_overrides[get_bot_instance] = lambda: mock_bot

    idempotency_key = str(uuid.uuid4())

    # Simulate a Telegram webhook update
    webhook_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1234567890,
            "text": "/start",
        },
    }

    # First webhook request
    response1 = await client.post(
        "/api/v1/webhook/",
        json=webhook_data,
        headers={
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response1.status_code == 200

    # Second webhook request with same idempotency key (simulating Telegram retry)
    response2 = await client.post(
        "/api/v1/webhook/",
        json=webhook_data,
        headers={
            "Idempotency-Key": idempotency_key,
        },
    )

    assert response2.status_code == 200

    # Both responses should be identical (cached response)
    assert response1.text == response2.text
    assert response1.status_code == response2.status_code


@pytest.mark.asyncio
async def test_webhook_idempotency_different_updates_processed_separately(
    client: AsyncClient,
    test_app: Any,
    mock_bot: Any,
):
    """Test that different webhook updates with different idempotency keys are processed separately."""
    # Override the Bot dependency with our mock
    test_app.dependency_overrides[get_bot_instance] = lambda: mock_bot

    idempotency_key1 = str(uuid.uuid4())
    idempotency_key2 = str(uuid.uuid4())

    webhook_data1 = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1234567890,
            "text": "/start",
        },
    }

    webhook_data2 = {
        "update_id": 987654321,
        "message": {
            "message_id": 2,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1234567891,
            "text": "/help",
        },
    }

    # First webhook with first key
    response1 = await client.post(
        "/api/v1/webhook/",
        json=webhook_data1,
        headers={
            "Idempotency-Key": idempotency_key1,
        },
    )

    assert response1.status_code == 200

    # Second webhook with different key
    response2 = await client.post(
        "/api/v1/webhook/",
        json=webhook_data2,
        headers={
            "Idempotency-Key": idempotency_key2,
        },
    )

    assert response2.status_code == 200


@pytest.mark.asyncio
async def test_webhook_without_idempotency_key_works(
    client: AsyncClient,
    test_app: Any,
    mock_bot: Any,
):
    """Test that webhook requests without idempotency key work normally."""
    # Override the Bot dependency with our mock
    test_app.dependency_overrides[get_bot_instance] = lambda: mock_bot

    webhook_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1234567890,
            "text": "/start",
        },
    }

    # Request without idempotency key
    response = await client.post(
        "/api/v1/webhook/",
        json=webhook_data,
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_webhook_idempotency_multiple_rapid_requests(
    client: AsyncClient,
    test_app: Any,
    mock_bot: Any,
):
    """Test that multiple rapid webhook requests with same key return cached response."""
    # Override the Bot dependency with our mock
    test_app.dependency_overrides[get_bot_instance] = lambda: mock_bot

    idempotency_key = str(uuid.uuid4())

    webhook_data = {
        "update_id": 123456789,
        "message": {
            "message_id": 1,
            "from": {
                "id": 123456789,
                "is_bot": False,
                "first_name": "Test",
                "username": "testuser",
            },
            "chat": {
                "id": 123456789,
                "first_name": "Test",
                "username": "testuser",
                "type": "private",
            },
            "date": 1234567890,
            "text": "/start",
        },
    }

    # Make multiple rapid requests with same idempotency key
    responses = []
    for _ in range(5):
        response = await client.post(
            "/api/v1/webhook/",
            json=webhook_data,
            headers={
                "Idempotency-Key": idempotency_key,
            },
        )
        responses.append(response)

    # All should succeed
    assert all(r.status_code == 200 for r in responses)

    # All should return the same response (cached)
    first_response_text = responses[0].text
    for response in responses[1:]:
        assert response.text == first_response_text
