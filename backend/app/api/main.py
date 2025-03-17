from fastapi import APIRouter

from app.api.routes import login, settings, utils, webhook, words

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(words.router)
api_router.include_router(webhook.router)
api_router.include_router(settings.router)
api_router.include_router(utils.router)
