from app.core.config import settings
from app.kafka.consumer import KafkaEventConsumer
from app.kafka.producer import KafkaEventProducer
from app.kafka.schemas import CardCreatedEvent, CardReviewedEvent

kafka_producer = KafkaEventProducer(
    bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    enabled=settings.KAFKA_ENABLED,
)

__all__ = [
    "CardCreatedEvent",
    "CardReviewedEvent",
    "KafkaEventConsumer",
    "KafkaEventProducer",
    "kafka_producer",
]
