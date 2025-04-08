from venv import logger

from fastapi import APIRouter, Header, HTTPException

from app.api.deps import TokensServiceDep, WordCardHandlerDep
from app.common.shemas.words import (
    NewCardRequest,
    NewCardResponce,
    ReviewRequest,
    ReviewResponse,
    WordResponse,
    WordsResponse,
)
from app.words.words_service import EndWordsInDb, EndWordsToReview

router = APIRouter(prefix="/cards", tags=["utils"])


@router.post("/", response_model=NewCardResponce, name="new_card", status_code=201)
async def new_card(
    request: NewCardRequest,
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
    authorization: str = Header(None),
):
    """Create for user new card"""
    try:
        created_card = await word_service.create_new_card(
            telegram_id=tokens_service.verify_access_token(token=authorization),
            known=request.known,
            word_id=request.word_id,
        )

        return NewCardResponce(**created_card.__dict__)

    except ValueError as e:
        logger.error("Error while creating new card: %s", e)
        raise HTTPException(status_code=400, detail=str(e)) from e

    except Exception as e:
        logger.error("Error while creating new card: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/", response_model=WordsResponse)
async def get_new_word(
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
    authorization: str = Header(None),
):
    """Get next new word for user to create card"""
    try:
        words = await word_service.get_new_words(
            user_id=tokens_service.verify_access_token(token=authorization)
        )
        word_responses = [
            WordResponse(
                word_id=word.id,
                word=word.native_word,
                translation=word.foreign_word,
                legend=word.legend,
            )
            for word in words
        ]
        return WordsResponse(words=word_responses)
    except EndWordsInDb as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    except Exception as e:
        logger.error("Error while getting new words: %s", e)
        raise HTTPException(status_code=500, detail="Internal server error") from e


@router.patch("/review/", response_model=ReviewResponse, status_code=201)
async def add_review(
    request: ReviewRequest,
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
    authorization: str = Header(None),
) -> ReviewResponse:
    """Add review to word card"""

    try:
        await word_service.add_review(
            user_id=tokens_service.verify_access_token(token=authorization),
            passed=request.passed,
            word_id=request.word_id,
        )
    except Exception as e:
        logger.error("Error while adding review: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error") from e

    return ReviewResponse(message="Review added successfully")


@router.get("/review/", response_model=WordsResponse)
async def get_review_words(
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
    authorization: str = Header(None),
) -> WordsResponse:
    try:
        words = await word_service.get_review_words(
            user_id=tokens_service.verify_access_token(token=authorization)
        )
        words = [
            WordResponse(
                word_id=word.id,
                word=word.native_word,
                translation=word.foreign_word,
                legend=word.legend,
            )
            for word in words
        ]
        return WordsResponse(words=words)

    except EndWordsToReview:
        return WordsResponse(words=[])

    except Exception as e:
        logger.error("Error while getting review words: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/review/count", response_model=int)
async def get_review_words_count(
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
    authorization: str = Header(None),
) -> int:
    """Get count of words available for review"""
    try:
        count = word_service.get_review_words_count(
            user_id=tokens_service.verify_access_token(token=authorization)
        )
        return count
    except Exception as e:
        logger.error("Error while getting review words count: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
