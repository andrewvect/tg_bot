# mypy: ignore-missing-imports
from dataclasses import dataclass, field

from sortedcontainers import SortedDict, SortedList, SortedSet  # type: ignore

from .idempotency import IdempotencyStore


@dataclass
class UserProfile:
    """Store user cards data"""

    # store words ids which user passed
    created_cards: SortedList = field(default_factory=SortedSet)
    # store words ids which user marked as known
    known_cards: SortedSet = field(default_factory=SortedSet)
    # store words ids which user makes 10 right reviews
    master_cards: SortedSet = field(default_factory=SortedSet)
    # store words ids which to review
    review_cards: list[int] = field(default_factory=list)
    # store words ids which user is waiting to review
    waiting_cards: SortedDict = field(default_factory=SortedDict)


users_states: dict[int, UserProfile] = {}

idempotency_store = IdempotencyStore(ttl_hours=24)
