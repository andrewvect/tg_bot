import logging
from typing import Any

logger = logging.getLogger(__name__)


async def handle_card_reviewed(event_data: dict[str, Any]) -> None:
    """Process a card review event from Kafka."""
    user_id = event_data.get("user_id")
    word_id = event_data.get("word_id")
    passed = event_data.get("passed")
    timestamp = event_data.get("timestamp")

    logger.info(
        "Processed card review event: user=%s, word=%s, passed=%s at %s",
        user_id,
        word_id,
        passed,
        timestamp,
    )


async def handle_card_created(event_data: dict[str, Any]) -> None:
    """Process a new card created event from Kafka."""
    user_id = event_data.get("user_id")
    word_id = event_data.get("word_id")
    known = event_data.get("known")
    timestamp = event_data.get("timestamp")

    logger.info(
        "Processed card created event: user=%s, word=%s, known=%s at %s",
        user_id,
        word_id,
        known,
        timestamp,
    )


async def dispatch_event(topic: str, event_data: dict[str, Any]) -> None:
    """Route message to specific topic handler."""
    event_type = event_data.get("event_type")
    if "review" in topic or event_type == "card_reviewed":
        await handle_card_reviewed(event_data)
    elif "created" in topic or event_type == "card_created":
        await handle_card_created(event_data)
    else:
        logger.warning("Unrecognized Kafka event on topic %s: %s", topic, event_data)
