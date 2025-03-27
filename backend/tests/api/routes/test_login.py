import pytest

# from sqlalchemy.orm import Session
# from sqlalchemy import select

# from app.core.config import settings
# from app.core.security import verify_password
# from app.models import User
# from app.utils import generate_password_reset_token


@pytest.mark.asyncio
async def test_get_access_token(
    client,
    test_user,  # noqa F811
    db_with_words,  # noqa F811
    db_session,  # noqa F811
    set_up_cache,  # noqa F811,
    mock_tokens_service,  # noqa F811
) -> None:
    responce = await client.post(
        "/api/v1/login/access-token", json={"init_data": "some_data"}
    )

    tokens = responce.json()
    assert responce.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
