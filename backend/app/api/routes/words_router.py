from fastapi import APIRouter, HTTPException, Security

from app.api.deps import WordCardHandlerDep, verify_token
from app.common.shemas.words import WordResponse, WordsResponse
from app.words.words_service import EndWordsInDb, EndWordsToReview

router = APIRouter(prefix="/words", tags=["words"])


@router.get("/", response_model=WordsResponse)
async def get_available_words(
    word_service: WordCardHandlerDep,
    user_id: int = Security(verify_token),
) -> WordsResponse:
    """Get available words for creating new cards"""
    try:
        words = await word_service.get_new_words(user_id=user_id)
        word_responses = [WordResponse.from_db_model(word) for word in words]
        return WordsResponse(words=word_responses)
    except EndWordsInDb as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@router.get("/reviews", response_model=WordsResponse)
async def get_words_for_review(
    word_service: WordCardHandlerDep,
    user_id: int = Security(verify_token),
) -> WordsResponse:
    """Get words that are due for review"""
    try:
        db_words = await word_service.get_review_words(user_id=user_id)
        word_responses = [WordResponse.from_db_model(
            word) for word in db_words]
        return WordsResponse(words=word_responses)

    except EndWordsToReview:
        return WordsResponse(words=[])
