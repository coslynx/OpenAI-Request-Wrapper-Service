import pytest
from fastapi.testclient import TestClient
from routers import user_router  # Import the user router
from models import UserSchema  # Import the user schema model
from utils.auth import create_access_token  # Import for authentication testing
from utils.db import Session, get_db  # Import for database mocking
from unittest.mock import MagicMock, patch
import bcrypt

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(user_router)
    return TestClient(app)

@pytest.mark.parametrize(
    "username, email, password, expected_message",
    [
        ("testuser", "test@example.com", "password123", "User registered successfully!"),
    ],
)
def test_register(client, username, email, password, expected_message, monkeypatch):
    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    mock_db.query.filter.first.return_value = None  # Simulate no existing user

    with patch('routers.user_router.get_db', return_value=mock_db):
        user_data = UserSchema(username=username, email=email, password=password)
        response = client.post("/users/register", json=user_data.dict())

        assert response.status_code == 201
        assert response.json()["message"] == expected_message
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()

@pytest.mark.parametrize(
    "username, email, password, existing_username, existing_email, expected_message",
    [
        ("testuser", "test@example.com", "password123", "testuser", None, "Username or email already exists."),
        (None, "test@example.com", "password123", None, "test@example.com", "Username or email already exists."),
    ],
)
def test_register_existing_user(
    client, username, email, password, existing_username, existing_email, expected_message, monkeypatch
):
    mock_db = MagicMock(spec=Session)
    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()
    mock_db.query.filter.first.return_value = User(
        username=existing_username, email=existing_email, hashed_password="hashed_password"
    )  # Simulate existing user

    with patch('routers.user_router.get_db', return_value=mock_db):
        user_data = UserSchema(username=username, email=email, password=password)
        response = client.post("/users/register", json=user_data.dict())

        assert response.status_code == 400
        assert response.json()["detail"] == expected_message
        mock_db.add.assert_not_called()
        mock_db.commit.assert_not_called()
        mock_db.refresh.assert_not_called()

@pytest.mark.parametrize(
    "username, password, expected_message",
    [
        ("testuser", "password123", "Incorrect username or password."),
    ],
)
def test_login_invalid_credentials(client, username, password, expected_message, monkeypatch):
    mock_db = MagicMock(spec=Session)
    mock_db.query.filter.first.return_value = User(
        username=username, email="test@example.com", hashed_password=bcrypt.hashpw("wrongpassword".encode(), bcrypt.gensalt()).decode()
    )

    with patch('routers.user_router.get_db', return_value=mock_db):
        user_data = UserSchema(username=username, password=password)
        response = client.post("/users/login", json=user_data.dict())

        assert response.status_code == 401
        assert response.json()["detail"] == expected_message

@pytest.mark.parametrize(
    "username, password, expected_message",
    [
        ("testuser", "password123", "User registered successfully!"),
    ],
)
def test_login(client, username, password, expected_message, monkeypatch):
    mock_db = MagicMock(spec=Session)
    mock_db.query.filter.first.return_value = User(
        username=username, email="test@example.com", hashed_password=bcrypt.hashpw("password123".encode(), bcrypt.gensalt()).decode()
    )

    with patch('routers.user_router.get_db', return_value=mock_db):
        user_data = UserSchema(username=username, password=password)
        response = client.post("/users/login", json=user_data.dict())

        assert response.status_code == 200
        assert response.json()["access_token"] is not None
        assert response.json()["token_type"] == "bearer"

@pytest.mark.parametrize(
    "username, email, expected_data",
    [
        ("testuser", "test@example.com", {"username": "testuser", "email": "test@example.com"}),
    ],
)
def test_get_current_user(client, username, email, expected_data, monkeypatch):
    mock_db = MagicMock(spec=Session)
    mock_db.query.filter.first.return_value = User(
        id=1, username=username, email=email, hashed_password="hashed_password"
    )
    mock_access_token = create_access_token(data={"sub": 1})

    with patch('routers.user_router.get_db', return_value=mock_db), patch(
        'routers.user_router.get_current_user', return_value=User(id=1, username=username, email=email)
    ):
        response = client.get("/users/me", headers={"Authorization": f"Bearer {mock_access_token}"})

        assert response.status_code == 200
        assert response.json() == expected_data

def test_get_current_user_unauthenticated(client, monkeypatch):
    response = client.get("/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"