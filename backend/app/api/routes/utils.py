from fastapi import APIRouter

router = APIRouter(prefix="/utils")


@router.get("/health-check/", tags=["Health Check"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint.
    """
    return {"status": "ok"}
