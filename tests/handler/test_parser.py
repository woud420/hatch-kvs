import pytest
from unittest.mock import MagicMock, patch
import json
from src.handler.parser import CommandParser
from src.model.response import Response

@pytest.fixture
def mock_api():
    with patch("src.handler.parser.KeyValueAPI") as MockAPI:
        mock_instance = MockAPI.return_value
        mock_instance.put.return_value = Response("Ok")
        mock_instance.get.return_value = Response("Ok", result="mocked_value")
        mock_instance.delete.return_value = Response("Ok", result="True")
        mock_instance.start.return_value = Response("Ok")
        mock_instance.commit.return_value = Response("Ok")
        mock_instance.rollback.return_value = Response("Ok")
        yield mock_instance

def test_empty_command(mock_api):
    """Test handling of an empty command."""
    parser = CommandParser()
    response = parser.parse("")
    assert json.loads(response) == {"status": "Error", "mesg": "Empty command. Available commands: PUT, GET, DEL, START, COMMIT, ROLLBACK"}

def test_put_command(mock_api):
    """Test PUT command with correct arguments."""
    parser = CommandParser()
    response = parser.parse("PUT key1 value1")
    assert json.loads(response) == {"status": "Ok"}

def test_get_command_existing_key(mock_api):
    """Test GET command for an existing key."""
    parser = CommandParser()
    response = parser.parse("GET key1")
    assert json.loads(response) == {"status": "Ok", "result": "mocked_value"}

def test_get_command_non_existent_key(mock_api):
    """Test GET command for a key that does not exist."""
    mock_api.get.return_value = Response("Error", mesg="Key not found")
    parser = CommandParser()
    response = parser.parse("GET missing_key")
    assert json.loads(response) == {"status": "Error", "mesg": "Key not found"}

def test_delete_command_existing_key(mock_api):
    """Test DELETE command for an existing key."""
    parser = CommandParser()
    response = parser.parse("DEL key1")
    assert json.loads(response) == {"status": "Ok", "result": "True"}

def test_delete_command_non_existent_key(mock_api):
    """Test DELETE command for a non-existent key."""
    mock_api.delete.return_value = Response("Error", mesg="Key not found")
    parser = CommandParser()
    response = parser.parse("DEL missing_key")
    assert json.loads(response) == {"status": "Error", "mesg": "Key not found"}

def test_start_transaction(mock_api):
    """Test START command."""
    parser = CommandParser()
    response = parser.parse("START")
    assert json.loads(response) == {"status": "Ok"}

def test_commit_transaction(mock_api):
    """Test COMMIT command."""
    parser = CommandParser()
    response = parser.parse("COMMIT")
    assert json.loads(response) == {"status": "Ok"}

def test_rollback_transaction(mock_api):
    """Test ROLLBACK command."""
    parser = CommandParser()
    response = parser.parse("ROLLBACK")
    assert json.loads(response) == {"status": "Ok"}

def test_unknown_command(mock_api):
    """Test handling of an unknown command."""
    parser = CommandParser()
    response = parser.parse("UNKNOWN")
    assert json.loads(response) == {"status": "Error", "mesg": "Unknown command 'UNKNOWN'. Available commands: PUT, GET, DEL, START, COMMIT, ROLLBACK"}

def test_exception_handling(mock_api):
    """Test that an exception inside the API is properly caught."""
    mock_api.put.side_effect = Exception("Unexpected Error")
    parser = CommandParser()
    response = parser.parse("PUT key1 value1")
    assert json.loads(response) == {"status": "Error", "mesg": "Unexpected Error"}

