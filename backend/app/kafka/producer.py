import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class KafkaEventProducer:
    """Asynchronous Kafka event producer with graceful fallback."""

    def __init__(self, bootstrap_servers: str, enabled: bool = True):
        self.bootstrap_servers = bootstrap_servers
        self.enabled = enabled
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        if not self.enabled:
            logger.info("Kafka is disabled; producer not started.")
            return

        try:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
            )
            await self._producer.start()
            logger.info("Kafka producer connected to %s", self.bootstrap_servers)
        except Exception as exc:
            logger.warning(
                "Kafka producer failed to connect to %s: %s. Operating in degraded mode.",
                self.bootstrap_servers,
                exc,
            )
            self._producer = None

    async def stop(self) -> None:
        if self._producer:
            try:
                await self._producer.stop()
                logger.info("Kafka producer stopped successfully.")
            except Exception as exc:
                logger.warning("Error stopping Kafka producer: %s", exc)
            finally:
                self._producer = None

    async def publish(
        self,
        topic: str,
        event: BaseModel | dict[str, Any],
        key: str | None = None,
    ) -> bool:
        if not self.enabled:
            logger.debug("Kafka disabled, skipping event to %s", topic)
            return False

        if not self._producer:
            logger.warning("Kafka producer unavailable; event dropped for %s", topic)
            return False

        try:
            payload = event.model_dump() if isinstance(event, BaseModel) else event
            key_bytes = key.encode("utf-8") if key else None
            await self._producer.send_and_wait(topic, value=payload, key=key_bytes)
            logger.info(
                "Successfully published Kafka event to %s (key=%s): %s",
                topic,
                key,
                payload,
            )
            return True
        except Exception as exc:
            logger.error("Failed to publish Kafka event to %s: %s", topic, exc)
            return False
