import pytest
from utils.auth import create_access_token, get_current_user
from utils.db import Session, get_db, User, create_user
from models.user_schema import UserSchema
from unittest.mock import MagicMock, patch
import bcrypt

@pytest.fixture
def mock_db():
    mock_session = MagicMock(spec=Session)
    mock_session.query.filter.first.return_value = None
    mock_session.add = MagicMock()
    mock_session.commit = MagicMock()
    mock_session.refresh = MagicMock()
    return mock_session

@pytest.fixture
def test_user(mock_db):
    user_data = UserSchema(username="testuser", email="test@example.com", password="password123")
    test_user = create_user(mock_db, user_data)
    return test_user

def test_create_access_token(test_user):
    token = create_access_token(data={"sub": test_user.id})
    assert isinstance(token, str)
    assert token.split(".")

def test_get_current_user(test_user, mock_db):
    token = create_access_token(data={"sub": test_user.id})
    with patch('utils.auth.get_db', return_value=mock_db):
        mock_db.query.filter.first.return_value = test_user
        user = get_current_user(token=token)
        assert user.id == test_user.id

def test_get_current_user_invalid_token(mock_db):
    token = "invalid_token"
    with patch('utils.auth.get_db', return_value=mock_db):
        with pytest.raises(Exception) as e:
            get_current_user(token=token)
        assert "Invalid token" in str(e.value)

def test_get_current_user_expired_token(mock_db):
    token = create_access_token(data={"sub": 1}, expires_delta=timedelta(seconds=-1))
    with patch('utils.auth.get_db', return_value=mock_db):
        with pytest.raises(Exception) as e:
            get_current_user(token=token)
        assert "Token expired" in str(e.value)

def test_create_user(mock_db):
    user_data = UserSchema(username="testuser", email="test@example.com", password="password123")
    user = create_user(mock_db, user_data)
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert bcrypt.checkpw(user_data.password.encode(), user.hashed_password.encode())
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_get_user_by_username(mock_db, test_user):
    with patch('utils.db.get_user_by_username', return_value=test_user):
        user = get_user_by_username(mock_db, test_user.username)
        assert user.id == test_user.id

def test_get_user_by_email(mock_db, test_user):
    with patch('utils.db.get_user_by_email', return_value=test_user):
        user = get_user_by_email(mock_db, test_user.email)
        assert user.id == test_user.id

def test_create_request(mock_db, test_user):
    request_data = RequestSchema(model="gpt-3.5-turbo", prompt="Hello world", parameters={})
    request = create_request(mock_db, request_data, test_user.id)
    assert request.model == "gpt-3.5-turbo"
    assert request.prompt == "Hello world"
    assert request.parameters == {}
    assert request.user_id == test_user.id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()

def test_get_requests_by_user(mock_db, test_user):
    with patch('utils.db.get_requests_by_user', return_value=[1, 2, 3]):
        requests = get_requests_by_user(mock_db, test_user.id)
        assert requests == [1, 2, 3]

def test_get_request_by_id(mock_db, test_user):
    with patch('utils.db.get_request_by_id', return_value=1):
        request = get_request_by_id(mock_db, 1)
        assert request == 1

def test_initialize_db(mock_db):
    initialize_db(mock_db)
    mock_db.create_all.assert_called_once()