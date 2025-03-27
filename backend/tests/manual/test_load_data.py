import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("db_with_words", [{"count": 200}], indirect=True)
async def test_load_words(db_with_words):
    # Verify the number of words created
    assert len(db_with_words) == 200
    assert 1 == 1
