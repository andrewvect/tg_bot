from typing import Annotated
from venv import logger

from fastapi import APIRouter, Cookie, Depends, HTTPException, Request

from app.api.deps import WordCardHandlerDep, TokensServiceDep, get_tokens_service
from app.common.shemas.words import (
    NewCardRequest,
    ReviewRequest,
    ReviewResponse,
    WordResponse,
    WordsResponse,
)
from app.words.words_service import EndWordsInDb, EndWordsToReview

router = APIRouter(prefix="/cards", tags=["utils"])


@router.post("/", name="new_card")
async def new_card(
    request: NewCardRequest,
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
    token:  Annotated[str | None, Cookie()] = None,
):
    
    """Create for user new card"""
    try:
        await word_service.create_new_card(
            telegram_id=tokens_service.get_current_user(token=token),
            known=request.known,
        )
    except Exception as e:
        logger.error("Error while creating new card: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(
            "Internal server error")) from e
    return {"message": "Word card created successfully"}


@router.get("/", response_model=WordsResponse)
async def get_new_word(
    request: Request,
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
    token: Annotated[str | None, Cookie()] = None
):
    """Get next new word for user to create card"""
    try:
        words = await word_service.get_new_words(
            user_id=tokens_service.get_current_user(token=token)
        )
    except EndWordsInDb as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error("Error while getting new words: %s", e)
        raise HTTPException(status_code=500, detail=str(
            "Internal server error")) from e
    return {"words": words}


@router.post("/review/", response_model=ReviewResponse)
async def add_review(
    request: ReviewRequest,
    token: Annotated[str | None, Cookie()],
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
) -> ReviewResponse:
    """Add review to word card"""

    try:
        await word_service.add_review(
            user_id=tokens_service.get_current_user(token=token), passed=request.passed
        )
    except Exception as e:
        logger.error("Error while adding review: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail=str(
            "Internal server error")) from e

    return {"message": "Review added successfully"}


@router.get("/review", response_model=WordsResponse)
async def get_review_words(
    token: Annotated[str | None, Cookie()],
    word_service: WordCardHandlerDep,
    tokens_service: TokensServiceDep,
) -> WordsResponse:
    """Get review words for user default is 20"""

    try:
        words = await word_service.get_review_words(
            user_id=tokens_service.get_current_user(token=token)
        )
    except EndWordsToReview as e:
        raise HTTPException(status_code=400, detail=str("No words to review"))
    except Exception as e:
        logger.error("Error while getting review words: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500, detail=str("Internal server error"))
    else:
        return {"words": words}
