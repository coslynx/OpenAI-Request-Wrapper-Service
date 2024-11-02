import pytest
from fastapi.testclient import TestClient
from routers import request_router  # Import the request router
from models import RequestSchema  # Import the request schema model
from utils.openai import openai_request  # Import for mocking
from utils.db import Session  # Import for database mocking
from utils.db import get_db  # Import for database dependency injection
from unittest.mock import MagicMock, patch

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(request_router)
    return TestClient(app)

@pytest.mark.parametrize(
    "model, prompt, parameters, expected_response",
    [
        ("gpt-3.5-turbo", "Hello world", {}, "Hello, world!"),
        ("text-davinci-003", "What is the meaning of life?", {"temperature": 0.7}, "The meaning of life is a complex question..."),
    ],
)
def test_create_request(client, model, prompt, parameters, expected_response, monkeypatch):
    """Tests the 'create_request' endpoint with various model, prompt, and parameters."""

    mock_openai_response = expected_response

    def mock_openai_request(*args, **kwargs):
        return mock_openai_response

    monkeypatch.setattr(openai_request, "openai_request", mock_openai_request)

    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    with patch('routers.request_router.get_db', return_value=mock_db):
        request_data = RequestSchema(model=model, prompt=prompt, parameters=parameters)
        response = client.post("/requests/create", json=request_data.dict())

        assert response.status_code == 200
        assert response.json() == {"message": "Request created successfully!", "request_id": 1}  # Mock response
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

def test_create_request_invalid_model(client, monkeypatch):
    """Tests the 'create_request' endpoint with an invalid OpenAI model."""

    mock_openai_response = "Error"

    def mock_openai_request(*args, **kwargs):
        return mock_openai_response

    monkeypatch.setattr(openai_request, "openai_request", mock_openai_request)

    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    with patch('routers.request_router.get_db', return_value=mock_db):
        request_data = RequestSchema(model="invalid_model", prompt="Hello world", parameters={})
        response = client.post("/requests/create", json=request_data.dict())

        assert response.status_code == 422  # Validation error
        assert response.json() == {"detail": [{"loc": ['model'], "msg": 'value is not a valid choice', "type": 'type_error.choice', "ctx": {'choices': ['gpt-3.5-turbo', 'text-davinci-003', 'text-curie-001', 'text-babbage-001', 'text-ada-001']}}]}

def test_create_request_openai_error(client, monkeypatch):
    """Tests the 'create_request' endpoint when the OpenAI API call fails."""

    def mock_openai_request(*args, **kwargs):
        raise openai.error.APIError("Error while making OpenAI request.")

    monkeypatch.setattr(openai_request, "openai_request", mock_openai_request)

    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    with patch('routers.request_router.get_db', return_value=mock_db):
        request_data = RequestSchema(model="gpt-3.5-turbo", prompt="Hello world", parameters={})
        response = client.post("/requests/create", json=request_data.dict())

        assert response.status_code == 500
        assert response.json() == {"detail": "OpenAI API Error: Error while making OpenAI request."}