from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr
from aiogram import Bot, Dispatcher, types

from app.api.deps import get_current_active_superuser
from app.models import Message
from app.utils import generate_test_email, send_email

router = APIRouter(prefix="/webhook", tags=["utils"])

# router to get updates from telegram
@router.post('/')
async def get_updates():
    pass
