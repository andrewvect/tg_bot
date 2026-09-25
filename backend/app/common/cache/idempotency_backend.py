"""Bounded in-memory backend for the Idempotency-Key ASGI middleware.

The upstream ``MemoryBackend`` (asgi-idempotency-header) expires cached
*responses* after ``expiry`` seconds, but never expires or caps the set of
"request in flight" keys it tracks, and neither store has a maximum size.
Since this middleware runs on unauthenticated routes too (``/login/access-token``,
``/webhook/``), a client can grow both stores without bound simply by sending
unique ``Idempotency-Key`` headers, exhausting process memory over time.

This subclass adds a TTL for abandoned "in flight" markers and a hard cap on
how many entries either store may hold, evicting the oldest entry once full.
"""

import time
from dataclasses import dataclass, field
from typing import Any

from idempotency_header_middleware.backends.memory import MemoryBackend


@dataclass()
class BoundedMemoryBackend(MemoryBackend):
    pending_ttl_seconds: float = 60.0
    max_entries: int = 10_000
    _pending_since: dict[str, float] = field(default_factory=dict)

    def _evict_stale_pending(self) -> None:
        """Drop 'in flight' markers left behind by requests that never completed."""
        now = time.time()
        stale_keys = [
            key
            for key, started_at in self._pending_since.items()
            if now - started_at > self.pending_ttl_seconds
        ]
        for key in stale_keys:
            self.keys.discard(key)
            del self._pending_since[key]

    def _evict_oldest_pending_if_full(self) -> None:
        if len(self.keys) >= self.max_entries and self._pending_since:
            oldest_key = min(self._pending_since, key=self._pending_since.__getitem__)
            self.keys.discard(oldest_key)
            del self._pending_since[oldest_key]

    def _evict_oldest_response_if_full(self) -> None:
        if len(self.response_store) >= self.max_entries:
            oldest_key = next(iter(self.response_store))
            del self.response_store[oldest_key]

    async def store_idempotency_key(self, idempotency_key: str) -> bool:
        self._evict_stale_pending()
        already_pending = await super().store_idempotency_key(idempotency_key)
        if not already_pending:
            self._evict_oldest_pending_if_full()
            self._pending_since[idempotency_key] = time.time()
        return already_pending

    async def clear_idempotency_key(self, idempotency_key: str) -> None:
        await super().clear_idempotency_key(idempotency_key)
        self._pending_since.pop(idempotency_key, None)

    async def store_response_data(
        self, idempotency_key: str, payload: dict[str, Any], status_code: int
    ) -> None:
        self._evict_oldest_response_if_full()
        await super().store_response_data(idempotency_key, payload, status_code)
        # A completed, cached response means the key is no longer "in flight";
        # the base implementation never clears it, which otherwise makes a
        # key unusable forever after its cached response eventually expires.
        self.keys.discard(idempotency_key)
        self._pending_since.pop(idempotency_key, None)
