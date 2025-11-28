"""
Idempotency store for API endpoints.
"""
from datetime import datetime, timedelta, timezone
from typing import Any


class IdempotencyStore:
    """
    In-memory store for idempotency keys with TTL support.
    Stores idempotency keys with their responses to ensure idempotent operations.
    """

    def __init__(self, ttl_hours: int = 24):
        """
        Initialize idempotency store.

        Args:
            ttl_hours: Time-to-live for stored keys in hours (default: 24)
        """
        self._store: dict[str, tuple[datetime, Any, int]] = {}
        self.ttl_hours = ttl_hours

    def _cleanup_expired(self) -> None:
        """Remove expired entries from the store (lazy cleanup)."""
        now = datetime.now(timezone.utc)
        expired_keys = [
            key
            for key, (timestamp, _, _) in self._store.items()
            if now - timestamp > timedelta(hours=self.ttl_hours)
        ]
        for key in expired_keys:
            del self._store[key]

    def check(self, idempotency_key: str, user_id: int) -> Any | None:
        """
        Check if idempotency key exists and return cached response.

        Args:
            idempotency_key: Unique key from client
            user_id: User ID to ensure user-scoped idempotency

        Returns:
            Cached response if key exists and is valid, None otherwise
        """
        # Lazy cleanup on each check
        self._cleanup_expired()

        # Combine user_id with key for user-scoped lookup
        scoped_key = f"{user_id}:{idempotency_key}"

        if scoped_key not in self._store:
            return None

        timestamp, response, stored_user_id = self._store[scoped_key]

        # Verify user_id matches (prevent cross-user replay)
        if stored_user_id != user_id:
            return None

        # Verify not expired
        if datetime.now(timezone.utc) - timestamp > timedelta(hours=self.ttl_hours):
            del self._store[scoped_key]
            return None

        return response

    def store(self, idempotency_key: str, user_id: int, response: Any) -> None:
        """
        Store response with idempotency key.

        Args:
            idempotency_key: Unique key from client
            user_id: User ID for user-scoped idempotency
            response: Response object to cache
        """
        # Combine user_id with key to ensure user-scoped storage
        scoped_key = f"{user_id}:{idempotency_key}"
        self._store[scoped_key] = (
            datetime.now(timezone.utc), response, user_id)

    def clear(self) -> None:
        """Clear all stored keys (useful for testing)."""
        self._store.clear()

    def size(self) -> int:
        """Return the number of stored keys."""
        return len(self._store)
