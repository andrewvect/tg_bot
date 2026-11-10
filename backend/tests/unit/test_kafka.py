import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import BaseModel

from app.kafka.consumer import KafkaEventConsumer
from app.kafka.handlers import (
    dispatch_event,
    handle_card_created,
    handle_card_reviewed,
)
from app.kafka.producer import KafkaEventProducer
from app.kafka.schemas import CardCreatedEvent, CardReviewedEvent


class SampleEvent(BaseModel):
    message: str
    code: int


# --- 1. Schemas Tests ---


def test_card_reviewed_event_schema():
    event = CardReviewedEvent(user_id=123, word_id=456, passed=True)
    assert event.user_id == 123
    assert event.word_id == 456
    assert event.passed is True
    assert event.event_type == "card_reviewed"
    assert isinstance(event.timestamp, datetime)

    dumped = event.model_dump()
    assert dumped["user_id"] == 123
    assert dumped["word_id"] == 456
    assert dumped["passed"] is True
    assert dumped["event_type"] == "card_reviewed"


def test_card_created_event_schema():
    event = CardCreatedEvent(user_id=789, word_id=101, known=False)
    assert event.user_id == 789
    assert event.word_id == 101
    assert event.known is False
    assert event.event_type == "card_created"
    assert isinstance(event.timestamp, datetime)


# --- 2. Producer Tests ---


@pytest.mark.asyncio
async def test_producer_disabled():
    producer = KafkaEventProducer(bootstrap_servers="localhost:9092", enabled=False)
    await producer.start()
    assert producer._producer is None

    result = await producer.publish("test-topic", {"data": 123})
    assert result is False

    await producer.stop()
    assert producer._producer is None


@pytest.mark.asyncio
async def test_producer_start_and_publish_success():
    producer = KafkaEventProducer(bootstrap_servers="localhost:9092", enabled=True)

    mock_aiokafka = AsyncMock()
    mock_aiokafka.start = AsyncMock()
    mock_aiokafka.stop = AsyncMock()
    mock_aiokafka.send_and_wait = AsyncMock()

    with patch("app.kafka.producer.AIOKafkaProducer", return_value=mock_aiokafka):
        await producer.start()
        assert producer._producer is not None
        mock_aiokafka.start.assert_awaited_once()

        event = SampleEvent(message="hello", code=200)
        published = await producer.publish(
            topic="test-topic", event=event, key="user-1"
        )
        assert published is True
        mock_aiokafka.send_and_wait.assert_awaited_once_with(
            "test-topic",
            value={"message": "hello", "code": 200},
            key=b"user-1",
        )

        await producer.stop()
        mock_aiokafka.stop.assert_awaited_once()
        assert producer._producer is None


@pytest.mark.asyncio
async def test_producer_connection_failure_graceful():
    producer = KafkaEventProducer(bootstrap_servers="bad-host:9092", enabled=True)

    with patch(
        "app.kafka.producer.AIOKafkaProducer.start",
        side_effect=Exception("Connection refused"),
    ):
        # Should not raise exception
        await producer.start()
        assert producer._producer is None

        # Publishing when not connected returns False
        result = await producer.publish("test-topic", {"data": 1})
        assert result is False


@pytest.mark.asyncio
async def test_producer_publish_exception_handled():
    producer = KafkaEventProducer(bootstrap_servers="localhost:9092", enabled=True)
    mock_aiokafka = AsyncMock()
    mock_aiokafka.send_and_wait = AsyncMock(side_effect=Exception("Kafka timeout"))
    producer._producer = mock_aiokafka

    result = await producer.publish("test-topic", {"key": "val"})
    assert result is False


# --- 3. Consumer Tests ---


@pytest.mark.asyncio
async def test_consumer_disabled():
    consumer = KafkaEventConsumer(
        topics=["test-topic"],
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        enabled=False,
    )
    handler = AsyncMock()
    await consumer.start(handler)
    assert consumer._consumer is None
    await consumer.stop()


@pytest.mark.asyncio
async def test_consumer_start_and_stop():
    consumer = KafkaEventConsumer(
        topics=["test-topic"],
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        enabled=True,
    )

    mock_aiokafka_consumer = AsyncMock()
    mock_aiokafka_consumer.start = AsyncMock()
    mock_aiokafka_consumer.stop = AsyncMock()

    # Mock async iterator for consumer
    async def empty_iterator():
        if False:
            yield

    mock_aiokafka_consumer.__aiter__.side_effect = empty_iterator

    with patch(
        "app.kafka.consumer.AIOKafkaConsumer", return_value=mock_aiokafka_consumer
    ):
        handler = AsyncMock()
        await consumer.start(handler)
        assert consumer._running is True
        mock_aiokafka_consumer.start.assert_awaited_once()

        await consumer.stop()
        assert consumer._running is False
        mock_aiokafka_consumer.stop.assert_awaited_once()


@pytest.mark.asyncio
async def test_consumer_consume_loop():
    consumer = KafkaEventConsumer(
        topics=["test-topic"],
        bootstrap_servers="localhost:9092",
        group_id="test-group",
        enabled=True,
    )

    mock_message = MagicMock()
    mock_message.topic = "flashcard-reviews"
    mock_message.partition = 0
    mock_message.offset = 12
    mock_message.value = {"user_id": 1, "passed": True}

    async def mock_msg_generator():
        yield mock_message
        await asyncio.sleep(0.01)

    mock_aiokafka_consumer = AsyncMock()
    mock_aiokafka_consumer.__aiter__.side_effect = mock_msg_generator
    consumer._consumer = mock_aiokafka_consumer
    consumer._running = True

    handler = AsyncMock()
    consumer._task = asyncio.create_task(consumer._consume_loop(handler))

    await asyncio.sleep(0.05)
    await consumer.stop()

    handler.assert_awaited_once_with(
        "flashcard-reviews", {"user_id": 1, "passed": True}
    )


# --- 4. Handlers Tests ---


@pytest.mark.asyncio
async def test_handlers_dispatch():
    with patch(
        "app.kafka.handlers.handle_card_reviewed", new_callable=AsyncMock
    ) as mock_rev:
        await dispatch_event("flashcard-reviews", {"user_id": 1, "passed": True})
        mock_rev.assert_awaited_once_with({"user_id": 1, "passed": True})

    with patch(
        "app.kafka.handlers.handle_card_created", new_callable=AsyncMock
    ) as mock_created:
        await dispatch_event("flashcard-created", {"user_id": 2, "word_id": 5})
        mock_created.assert_awaited_once_with({"user_id": 2, "word_id": 5})

    with patch(
        "app.kafka.handlers.handle_card_reviewed", new_callable=AsyncMock
    ) as mock_rev:
        await dispatch_event(
            "custom-topic", {"event_type": "card_reviewed", "user_id": 3}
        )
        mock_rev.assert_awaited_once_with({"event_type": "card_reviewed", "user_id": 3})


@pytest.mark.asyncio
async def test_handle_card_reviewed_and_created():
    # Should execute without errors
    await handle_card_reviewed(
        {
            "user_id": 10,
            "word_id": 20,
            "passed": True,
            "timestamp": "2026-11-10T00:00:00",
        }
    )
    await handle_card_created(
        {
            "user_id": 10,
            "word_id": 20,
            "known": False,
            "timestamp": "2026-11-10T00:00:00",
        }
    )


# --- 5. Route Integration Tests ---


@pytest.mark.asyncio
async def test_new_card_route_publishes_kafka_event():
    from app.api.routes.words import new_card
    from app.common.shemas.words import NewCardRequest

    class DummyCard:
        def __init__(self):
            self.id = 1
            self.word_id = 10
            self.user_id = 42
            self.count_of_views = 1
            self.last_view = datetime.now()

    mock_word_service = AsyncMock()
    mock_word_service.create_new_card = AsyncMock(return_value=DummyCard())

    mock_producer = AsyncMock()
    mock_producer.publish = AsyncMock(return_value=True)

    request = NewCardRequest(word_id=10, known=False)
    resp = await new_card(
        request=request,
        word_service=mock_word_service,
        kafka_producer=mock_producer,
        user_id=42,
    )

    assert resp.word_id == 10
    mock_producer.publish.assert_awaited_once()
    _, kwargs = mock_producer.publish.call_args
    assert kwargs["topic"] == "flashcard-created"
    assert kwargs["event"].user_id == 42
    assert kwargs["event"].word_id == 10
    assert kwargs["event"].known is False
    assert kwargs["key"] == "42"


@pytest.mark.asyncio
async def test_add_review_route_publishes_kafka_event():
    from app.api.routes.words import add_review
    from app.common.shemas.words import ReviewRequest

    mock_word_service = AsyncMock()
    mock_idempotency_store = MagicMock()
    mock_idempotency_store.check.return_value = None

    mock_producer = AsyncMock()
    mock_producer.publish = AsyncMock(return_value=True)

    request = ReviewRequest(word_id=25, passed=True, idempotency_key="key-abc")
    resp = await add_review(
        request=request,
        word_service=mock_word_service,
        idempotency_store=mock_idempotency_store,
        kafka_producer=mock_producer,
        user_id=77,
    )

    assert resp.message == "Review added successfully"
    mock_producer.publish.assert_awaited_once()
    _, kwargs = mock_producer.publish.call_args
    assert kwargs["topic"] == "flashcard-reviews"
    assert kwargs["event"].user_id == 77
    assert kwargs["event"].word_id == 25
    assert kwargs["event"].passed is True
    assert kwargs["key"] == "77"
