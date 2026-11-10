import datetime

from pydantic import BaseModel, Field


class CardReviewedEvent(BaseModel):
    """Event published when a user reviews a flashcard."""

    user_id: int
    word_id: int
    passed: bool
    count_of_views: int | None = None
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    event_type: str = "card_reviewed"


class CardCreatedEvent(BaseModel):
    """Event published when a user creates a new flashcard."""

    user_id: int
    word_id: int
    known: bool
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc)
    )
    event_type: str = "card_created"
