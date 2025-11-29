from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.common.db.models.sentence import Sentence
    from app.common.db.models.word import Word


class ReviewRequest(BaseModel):
    passed: bool
    word_id: int
    idempotency_key: str


class ReviewResponse(BaseModel):
    message: str


class SentenceResponce(BaseModel):
    id: int
    native_text: str
    cyrilic_text: str
    latin_text: str

    @classmethod
    def from_db_model(cls, db_sentence: "Sentence") -> "SentenceResponce":
        """Convert a Sentence DB model to SentenceResponce schema."""
        return cls(
            id=db_sentence.id,
            native_text=db_sentence.native_text,
            cyrilic_text=db_sentence.cyrilic_text,
            latin_text=db_sentence.latin_text,
        )


class WordResponse(BaseModel):
    word_id: int
    latin_word: str
    cyrillic_word: str
    native_word: str
    legend: str | None = None
    sentences: list[SentenceResponce] | None = None

    @classmethod
    def from_db_model(cls, db_word: "Word") -> "WordResponse":
        """Convert a Word DB model to WordResponse schema."""
        return cls(
            word_id=db_word.id,
            latin_word=db_word.latin_word,
            cyrillic_word=db_word.cyrillic_word,
            native_word=db_word.native_word,
            legend=db_word.legend,
            sentences=[
                SentenceResponce.from_db_model(sentence)
                for sentence in db_word.sentences
            ]
            if db_word.sentences
            else [],
        )


class WordsResponse(BaseModel):
    words: list[WordResponse]


class NewCardRequest(BaseModel):
    known: bool
    word_id: int


class NewCardResponce(BaseModel):
    user_id: int
    word_id: int
    count_of_views: int
    last_view: datetime
    msg: str = "Word card created successfully"
