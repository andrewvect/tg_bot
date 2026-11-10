import asyncio
import logging
import signal

from app.core.config import settings
from app.kafka.consumer import KafkaEventConsumer
from app.kafka.handlers import dispatch_event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("kafka_worker")


async def main() -> None:
    topics = [
        settings.KAFKA_CARD_REVIEWS_TOPIC,
        settings.KAFKA_CARD_CREATED_TOPIC,
    ]
    logger.info("Initializing Kafka Worker for topics: %s", topics)

    consumer = KafkaEventConsumer(
        topics=topics,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_CONSUMER_GROUP,
        enabled=settings.KAFKA_ENABLED,
    )

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler() -> None:
        logger.info("Termination signal received. Shutting down worker...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except (NotImplementedError, RuntimeError):
            pass

    await consumer.start(dispatch_event)
    logger.info("Kafka Worker is listening for events...")

    try:
        await stop_event.wait()
    finally:
        logger.info("Stopping Kafka consumer...")
        await consumer.stop()
        logger.info("Kafka Worker stopped.")


if __name__ == "__main__":
    asyncio.run(main())
