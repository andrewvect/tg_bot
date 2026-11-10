import asyncio
import json
import logging
from collections.abc import Callable, Coroutine
from typing import Any

from aiokafka import AIOKafkaConsumer

logger = logging.getLogger(__name__)


class KafkaEventConsumer:
    """Asynchronous Kafka event consumer."""

    def __init__(
        self,
        topics: list[str],
        bootstrap_servers: str,
        group_id: str,
        enabled: bool = True,
        auto_offset_reset: str = "earliest",
    ):
        self.topics = topics
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.enabled = enabled
        self.auto_offset_reset = auto_offset_reset
        self._consumer: AIOKafkaConsumer | None = None
        self._running: bool = False
        self._task: asyncio.Task[None] | None = None

    async def start(
        self,
        handler: Callable[[str, dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None:
        if not self.enabled:
            logger.info("Kafka is disabled; consumer not started.")
            return

        try:
            self._consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                auto_offset_reset=self.auto_offset_reset,
                enable_auto_commit=True,
            )
            await self._consumer.start()
            self._running = True
            self._task = asyncio.create_task(self._consume_loop(handler))
            logger.info(
                "Kafka consumer started for topics %s (group=%s)",
                self.topics,
                self.group_id,
            )
        except Exception as exc:
            logger.warning(
                "Kafka consumer failed to connect to %s: %s. Degraded mode.",
                self.bootstrap_servers,
                exc,
            )
            self._consumer = None

    async def _consume_loop(
        self,
        handler: Callable[[str, dict[str, Any]], Coroutine[Any, Any, None]],
    ) -> None:
        if not self._consumer:
            return

        try:
            async for msg in self._consumer:
                if not self._running:
                    break
                try:
                    logger.debug(
                        "Received message on %s [%s] offset=%s",
                        msg.topic,
                        msg.partition,
                        msg.offset,
                    )
                    await handler(msg.topic, msg.value)
                except Exception as handler_err:
                    logger.error(
                        "Error in handler for topic %s: %s",
                        msg.topic,
                        handler_err,
                        exc_info=True,
                    )
        except asyncio.CancelledError:
            pass
        except Exception as exc:
            logger.error("Kafka consumer loop error: %s", exc, exc_info=True)

    async def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

        if self._consumer:
            try:
                await self._consumer.stop()
                logger.info("Kafka consumer stopped successfully.")
            except Exception as exc:
                logger.warning("Error stopping Kafka consumer: %s", exc)
            finally:
                self._consumer = None
