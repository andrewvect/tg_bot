"""Run backend server for frontnend end-to-end tests."""
from unittest.mock import Mock

from app.api.deps import get_tokens_service
from app.main import app

if __name__ == "__main__":
    import uvicorn

    mocker = Mock()
    mocker.verify_access_token.return_value = 2200240897
    mocker.verify.return_value = 2200240897
    app.dependency_overrides[get_tokens_service] = lambda: mocker

    uvicorn.run(app, host="localhost", port=8000)
