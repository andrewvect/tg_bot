import pytest
from sqlalchemy import select

from app.common.db.models import Settings


@pytest.mark.asyncio
async def test_get_user_settings(
    client,
    test_user,  # noqa F811
    test_user_settings,  # noqa F811
    db_session,  # noqa F811
    mock_tokens_service,  # noqa F811
):
    """Test getting user settings"""

    response = await client.get(
        "/api/v1/settings/", headers={"Authorization": "Bearer some_token"}
    )

    # check response
    assert response.status_code == 200
    assert response.json() == {
        "spoiler_settings": test_user_settings.spoiler_settings,
        "user_id": test_user.telegram_id,
        "alphabet_settings": test_user_settings.alphabet_settings,
    }


@pytest.mark.asyncio
async def test_set_user_settings(
    client,
    test_user,  # noqa F811
    test_user_settings,  # noqa F811
    db_session,  # noqa F811
    mock_tokens_service,  # noqa F811
):
    responce = await client.put(
        "/api/v1/settings/",
        headers={"Authorization": "Bearer some_token"},
        json={"spoiler_settings": 2, "alphabet_settings": 2},
    )

    assert responce.status_code == 200
    assert responce.json() == {
        "user_id": test_user.telegram_id,
        "spoiler_settings": 2,
        "alphabet_settings": 2,
    }
    # check db
    db_session.refresh(test_user_settings)
    settings = db_session.execute(
        select(Settings).where(Settings.user_id == test_user.telegram_id)
    )
    user_settings = settings.scalars().first()
    assert user_settings.spoiler_settings == 2
    assert user_settings.alphabet_settings == 2
