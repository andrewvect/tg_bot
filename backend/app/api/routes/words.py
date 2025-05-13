from venv import logger

# ensure Security is imported
from fastapi import APIRouter, HTTPException, Security

from app.api.deps import WordCardHandlerDep, verify_token
from app.common.shemas.words import (
    NewCardRequest,
    NewCardResponce,
    ReviewRequest,
    ReviewResponse,
    SentenceResponce,
    WordResponse,
    WordsResponse,
)
from app.words.words_service import EndWordsInDb, EndWordsToReview

router = APIRouter(prefix="/cards", tags=["utils"])


@router.post("/", response_model=NewCardResponce, name="new_card", status_code=201)
async def new_card(
    request: NewCardRequest,
    word_service: WordCardHandlerDep,
    user_id: int = Security(verify_token),
) -> NewCardResponce:
    """Create a new card for the user after verifying the token"""
    try:
        created_card = await word_service.create_new_card(
            telegram_id=user_id,
            known=request.known,
            word_id=request.word_id,
        )
        return NewCardResponce(**created_card.__dict__)
    except ValueError as e:
        logger.error("Error while creating new card: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/", response_model=WordsResponse)
async def get_new_word(
    word_service: WordCardHandlerDep,
    user_id: int = Security(verify_token),
) -> WordsResponse:
    """Get next new word for user to create card"""
    try:
        words = await word_service.get_new_words(user_id=user_id)
        word_responses = [
            WordResponse(
                word_id=word.id,
                latin_word=word.latin_word,
                cyrillic_word=word.cyrillic_word,
                native_word=word.native_word,
                legend=word.legend,
                sentences=[
                    SentenceResponce(
                        id=sentence.id,
                        native_text=sentence.native_text,
                        cyrilic_text=sentence.cyrilic_text,
                        latin_text=sentence.latin_text,
                    )
                    for sentence in word.sentences
                ]
                if word.sentences
                else [],
            )
            for word in words
        ]
        return WordsResponse(words=word_responses)
    except EndWordsInDb as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.patch("/review/", response_model=ReviewResponse, status_code=201)
async def add_review(
    request: ReviewRequest,
    word_service: WordCardHandlerDep,
    user_id: int = Security(verify_token),
) -> ReviewResponse:
    """Add review to word card"""

    await word_service.add_review(
        user_id=user_id,
        passed=request.passed,
        word_id=request.word_id,
    )

    return ReviewResponse(message="Review added successfully")


@router.get("/review/", response_model=WordsResponse)
async def get_review_words(
    word_service: WordCardHandlerDep,
    user_id: int = Security(verify_token),
) -> WordsResponse:
    try:
        db_words = await word_service.get_review_words(user_id=user_id)
        word_responses = [
            WordResponse(
                word_id=word.id,
                latin_word=word.latin_word,
                cyrillic_word=word.cyrillic_word,
                native_word=word.native_word,
                legend=word.legend,
                sentences=[
                    SentenceResponce(
                        id=sentence.id,
                        native_text=sentence.native_text,
                        cyrilic_text=sentence.cyrilic_text,
                        latin_text=sentence.latin_text,
                    )
                    for sentence in word.sentences
                ]
                if word.sentences
                else [],
            )
            for word in db_words
        ]
        return WordsResponse(words=word_responses)

    except EndWordsToReview:
        return WordsResponse(words=[])


@router.get("/review/count", response_model=int)
async def get_review_words_count(
    word_service: WordCardHandlerDep,
    user_id: int = Security(verify_token),
) -> int:
    """Get count of words available for review"""

    count = word_service.get_review_words_count(user_id=user_id)
    return count
