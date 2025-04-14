from datetime import datetime

from pydantic import BaseModel


class ReviewRequest(BaseModel):
    passed: bool
    word_id: int


class ReviewResponse(BaseModel):
    message: str


class SentenceResponce(BaseModel):
    id: int
    native_text: str
    cyrilic_text: str
    latin_text: str


class WordResponse(BaseModel):
    word_id: int
    latin_word: str
    cyrillic_word: str
    native_word: str
    legend: str | None = None
    sentences: list[SentenceResponce] | None = None


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
