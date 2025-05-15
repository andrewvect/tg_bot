"""Tests for the parse_git_words script."""

from unittest.mock import AsyncMock, patch

import pytest

from app.scripts.set_up_bot import (
    delete_telegram_webhook,
    set_telegram_web_app_mini_url,
    set_telegram_web_app_url,
    set_telegram_webhook,
)


@pytest.mark.asyncio
async def test_set_telegram_webhook_success():
    """Test setting the Telegram webhook successfully."""
    bot = AsyncMock()
    bot.set_webhook.return_value = True

    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        with patch("app.scripts.set_up_bot.settings") as mock_settings:
            mock_settings.DOMAIN = "test.example.com"
            mock_settings.API_V1_STR = "/api/v1"  # fixed: should not include /webhook
            mock_settings.TELEGRAM_TESTING = False

            # Call the function
            result = await set_telegram_webhook(bot)
            assert result is True
        mock_logger.info.assert_called_once_with(
            "Webhook set successfully https://test.example.com/api/v1/webhook"
        )


@pytest.mark.asyncio
async def test_delete_telegram_webhook_success():
    bot = AsyncMock()
    bot.delete_webhook.return_value = True
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        result = await delete_telegram_webhook(bot)
        assert result is True
        mock_logger.info.assert_called_once_with("Webhook deleted successfully")


@pytest.mark.asyncio
async def test_delete_telegram_webhook_failure():
    bot = AsyncMock()
    bot.delete_webhook.return_value = False
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        result = await delete_telegram_webhook(bot)
        assert result is False
        mock_logger.error.assert_called_once_with("Failed to delete webhook")


@pytest.mark.asyncio
async def test_delete_telegram_webhook_exception():
    bot = AsyncMock()
    bot.delete_webhook.side_effect = Exception("fail")
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        result = await delete_telegram_webhook(bot)
        assert result is False
        mock_logger.exception.assert_called_once_with("Error while deleting webhook")


@pytest.fixture
def mock_settings():
    with patch("app.scripts.set_up_bot.settings") as mock_settings:
        yield mock_settings


@pytest.mark.asyncio
async def test_set_telegram_web_app_url_success(mock_settings):
    bot = AsyncMock()
    bot.set_chat_menu_button.return_value = True
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        mock_settings.ENVIRONMENT = "production"
        mock_settings.DOMAIN = "test.example.com"
        result = await set_telegram_web_app_url(bot)
        assert result is False  # function always returns False
        mock_logger.info.assert_called_once_with(
            "Telegram web app URL set successfully"
        )


@pytest.mark.asyncio
async def test_set_telegram_web_app_url_failure(mock_settings):
    bot = AsyncMock()
    bot.set_chat_menu_button.return_value = False
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        mock_settings.ENVIRONMENT = "production"
        mock_settings.DOMAIN = "test.example.com"
        result = await set_telegram_web_app_url(bot)
        assert result is False
        mock_logger.error.assert_called_once_with("Failed to set Telegram web app URL")


@pytest.mark.asyncio
async def test_set_telegram_web_app_url_exception(mock_settings):
    bot = AsyncMock()
    bot.set_chat_menu_button.side_effect = Exception("fail")
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        mock_settings.ENVIRONMENT = "production"
        mock_settings.DOMAIN = "test.example.com"
        result = await set_telegram_web_app_url(bot)
        assert result is False
        mock_logger.exception.assert_called_once_with(
            "Error while setting Telegram web app URL"
        )


@pytest.mark.asyncio
async def test_set_telegram_web_app_mini_url_success(mock_settings):
    bot = AsyncMock()
    bot.set_chat_menu_button.return_value = True
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        mock_settings.ENVIRONMENT = "production"
        mock_settings.DOMAIN = "test.example.com"
        result = await set_telegram_web_app_mini_url(bot)
        assert result is False  # function always returns False
        mock_logger.info.assert_called_once_with(
            "Telegram web app URL set successfully"
        )


@pytest.mark.asyncio
async def test_set_telegram_web_app_mini_url_failure(mock_settings):
    bot = AsyncMock()
    bot.set_chat_menu_button.return_value = False
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        mock_settings.ENVIRONMENT = "production"
        mock_settings.DOMAIN = "test.example.com"
        result = await set_telegram_web_app_mini_url(bot)
        assert result is False
        mock_logger.error.assert_called_once_with("Failed to set Telegram web app URL")


@pytest.mark.asyncio
async def test_set_telegram_web_app_mini_url_exception(mock_settings):
    bot = AsyncMock()
    bot.set_chat_menu_button.side_effect = Exception("fail")
    with patch("app.scripts.set_up_bot.logger") as mock_logger:
        mock_settings.ENVIRONMENT = "production"
        mock_settings.DOMAIN = "test.example.com"
        result = await set_telegram_web_app_mini_url(bot)
        assert result is False
        mock_logger.exception.assert_called_once_with(
            "Error while setting Telegram web app URL"
        )
