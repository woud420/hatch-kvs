import pytest
from unittest.mock import MagicMock, patch
from src.api.kv_api import KeyValueAPI
from src.model.response import Response

@pytest.fixture
def mock_store():
    """Fixture to mock the datastore inside the KeyValueAPI singleton."""
    with patch.object(KeyValueAPI, "_instance", None):  # Reset singleton instance
        with patch("src.api.kv_api.KeyValueStore") as MockStore:
            mock_instance = MockStore.return_value
            mock_instance.get.return_value = None  # Default: key does not exist
            mock_instance.delete.return_value = False  # Default: deletion fails
            api = KeyValueAPI()  # Now it will use the mocked store
            api.store = mock_instance  # Ensure store is mocked inside singleton
            yield mock_instance

def test_singleton_instance(mock_store):
    """Test that KeyValueAPI follows the singleton pattern."""
    api1 = KeyValueAPI()
    api2 = KeyValueAPI()
    assert api1 is api2  # Singleton check

def test_put(mock_store):
    """Test that put() correctly forwards to the datastore."""
    api = KeyValueAPI()
    response = api.put("key1", "value1")
    assert response.status == "Ok"
    mock_store.put.assert_called_once_with("key1", "value1")

def test_get(mock_store):
    """Test that get() correctly fetches values from the datastore."""
    mock_store.get.return_value = "mocked_value"
    api = KeyValueAPI()
    response = api.get("key1")
    assert response.status == "Ok"
    assert response.result == "mocked_value"
    mock_store.get.assert_called_once_with("key1")

def test_delete(mock_store):
    """Test that delete() correctly calls the datastore."""
    mock_store.delete.return_value = True
    api = KeyValueAPI()
    response = api.delete("key1")
    assert response.status == "Ok"
    assert response.result is "True"
    mock_store.delete.assert_called_once_with("key1")

def test_start_transaction(mock_store):
    """Test that start() calls the datastore's start() method."""
    api = KeyValueAPI()
    response = api.start()
    assert response.status == "Ok"
    mock_store.start.assert_called_once()

def test_commit_transaction(mock_store):
    """Test that commit() calls the datastore's commit() method."""
    api = KeyValueAPI()
    response = api.commit()
    assert response.status == "Ok"
    mock_store.commit.assert_called_once()

def test_rollback_transaction(mock_store):
    """Test that rollback() calls the datastore's rollback() method."""
    api = KeyValueAPI()
    response = api.rollback()
    assert response.status == "Ok"
    mock_store.rollback.assert_called_once()

