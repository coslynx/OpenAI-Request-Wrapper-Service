import pytest
from fastapi.testclient import TestClient
from models import RequestSchema, UserSchema
from utils.auth import create_access_token
from utils.db import Session, get_db
from unittest.mock import MagicMock, patch
import bcrypt

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(request_router)
    return TestClient(app)

@pytest.mark.parametrize(
    "data, expected_result",
    [
        ({"model": "gpt-3.5-turbo", "prompt": "Hello world", "parameters": {}}, True),
        ({"model": "text-davinci-003", "prompt": "What is the meaning of life?", "parameters": {"temperature": 0.7}}, True),
        ({"model": "invalid_model", "prompt": "Hello world", "parameters": {}}, False),
        ({"model": "gpt-3.5-turbo", "prompt": "This prompt is much too long and exceeds the character limit.", "parameters": {}}, False),
        ({"model": "gpt-3.5-turbo", "prompt": "Hello world", "parameters": "invalid"}, False),
    ],
)
def test_request_schema_validation(data, expected_result):
    """Tests the validation rules for RequestSchema."""
    if expected_result:
        try:
            RequestSchema(**data)
        except ValueError:
            pytest.fail("Unexpected validation error")
    else:
        with pytest.raises(ValueError):
            RequestSchema(**data)

@pytest.mark.parametrize(
    "data, expected_result",
    [
        ({"username": "testuser", "email": "test@example.com", "password": "password123"}, True),
        ({"username": "testuser", "email": "test@example.com", "password": "pass"}, False),  # Short password
        ({"username": "testuser", "email": "invalid_email", "password": "password123"}, False),  # Invalid email
        ({"username": "", "email": "test@example.com", "password": "password123"}, False),  # Empty username
    ],
)
def test_user_schema_validation(data, expected_result):
    """Tests the validation rules for UserSchema."""
    if expected_result:
        try:
            UserSchema(**data)
        except ValueError:
            pytest.fail("Unexpected validation error")
    else:
        with pytest.raises(ValueError):
            UserSchema(**data)

def test_model_serialization():
    """Tests the serialization and deserialization of the Pydantic models."""
    request_data = RequestSchema(model="gpt-3.5-turbo", prompt="Hello world", parameters={"temperature": 0.5})
    user_data = UserSchema(username="testuser", email="test@example.com", password="password123")

    assert request_data.dict() == {
        "model": "gpt-3.5-turbo",
        "prompt": "Hello world",
        "parameters": {"temperature": 0.5}
    }
    assert user_data.dict() == {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }