import re
from pathlib import Path

import yaml
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.api.deps import async_session_factory
from app.common.db.repositories import SettingsRepo, UserRepo
from app.common.db.repositories.user import NewUser
from app.core.config import settings
from app.states.user import build_user_state
from app.utils.logger import logger

router = Router()

# Load content from YAML file


def load_content() -> dict:
    # Use absolute path for Docker compatibility
    content_path = Path("/app/content.yaml")
    if not content_path.exists():
        # fallback for local dev
        content_path = Path(__file__).parents[3] / "content.yaml"
    with open(content_path, encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


content = load_content()
messages = content.get("messages", {})


def markdown_to_html(text: str) -> str:
    """
    Convert Markdown-style formatting to HTML for Telegram.
    - **bold** becomes <b>bold</b>
    - [link text](url) becomes <a href="url">link text</a>
    """
    # Convert bold text: **text** -> <b>text</b>
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

    # Convert links: [text](url) -> <a href="url">text</a>
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r'<a href="\2">\1</a>', text)

    return text


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    """Send a message when the command /start is issued."""
    async with async_session_factory() as session:
        user_repo = UserRepo(session=session)
        settings_repo = SettingsRepo(session=session)
        try:
            await user_repo.create(
                user_name=message.from_user.username, telegram_id=message.from_user.id
            )
        except NewUser:
            logger.info(
                "User %s with ID %s registered",
                message.from_user.username,
                message.from_user.id,
            )
            # Notify admin about the new user registration

            if settings.ADMIN_TG_ID:
                admin_id = settings.ADMIN_TG_ID
                await message.bot.send_message(
                    admin_id,
                    messages.get("admin", {})
                    .get("new_user_registered", "")
                    .format(
                        username=message.from_user.username,
                        user_id=message.from_user.id,
                        user_url=f"tg://user?id={message.from_user.id}",
                    ),
                )
            await settings_repo.create_or_update_settings(user_id=message.from_user.id)
            await message.reply(
                messages.get("start", {})
                .get("new_user", "")
                .format(username=message.from_user.username)
            )
            states = await build_user_state()
            states.add_new_user(user_id=message.from_user.id)
        else:
            await message.reply(
                messages.get("start", {})
                .get("returning_user", "")
                .format(username=message.from_user.username)
            )


@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """Send a message when the command /help is issued."""
    help_sections = messages.get("help", {})

    # Send each help section as a separate message
    for section_name in ["intro", "usage", "features", "levels", "mot", "feedback"]:
        section_text = help_sections.get(section_name, "")
        if section_text:
            # Convert markdown formatting to HTML
            html_text = markdown_to_html(section_text)
            await message.answer(html_text, parse_mode="HTML")
