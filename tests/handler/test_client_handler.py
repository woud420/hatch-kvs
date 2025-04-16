import pytest
import socket
import threading
from unittest.mock import MagicMock, patch
from src.handler.client_handler import ClientHandler
from src.model.response import Response

@pytest.fixture
def mock_socket():
    """Fixture to provide a mock socket."""
    mock_sock = MagicMock(spec=socket.socket)
    return mock_sock

@pytest.fixture
def mock_parser():
    """Fixture to provide a mock CommandParser."""
    with patch("src.handler.client_handler.CommandParser") as MockParser:
        mock_instance = MockParser.return_value
        mock_instance.parse.side_effect = lambda cmd: str(Response("Ok", result=f"Response for {cmd.strip()}"))
        yield mock_instance

def test_client_handler_receives_data_and_sends_response(mock_socket, mock_parser):
    """Test that ClientHandler reads data from socket, processes it, and sends response."""
    mock_socket.recv.side_effect = [b"GET key1\n", b"exit\n"]  # Simulated received data

    handler = ClientHandler(mock_socket, ("127.0.0.1", 12345))
    handler.run()  # Run the handler

    # Ensure parse() was called with both commands
    mock_parser.parse.assert_any_call("GET key1\n")
    mock_parser.parse.assert_any_call("exit\n")

    # Ensure responses were sent for both commands
    expected_response = str(Response("Ok", result="Response for GET key1")) + "\n"
    exit_response = str(Response("Ok", result="Response for exit")) + "\n"

    assert mock_socket.send.call_count == 2
    mock_socket.send.assert_any_call(expected_response.encode("utf-8"))  # First response
    mock_socket.send.assert_any_call(exit_response.encode("utf-8"))  # Exit response

    # Ensure socket was closed at the end
    mock_socket.close.assert_called_once()

def test_client_handler_handles_disconnection(mock_socket, mock_parser):
    """Test that ClientHandler correctly handles client disconnection."""
    mock_socket.recv.side_effect = [b"HELLO\n", b""]  # Simulate disconnection after first message

    handler = ClientHandler(mock_socket, ("127.0.0.1", 12345))
    handler.run()  # Run the handler

    mock_parser.parse.assert_called_with("HELLO\n")  # Ensure parser received the command
    expected_response = str(Response("Ok", result="Response for HELLO")) + "\n"
    mock_socket.send.assert_called_with(expected_response.encode("utf-8"))  # Ensure response was sent
    mock_socket.close.assert_called_once()  # Ensure socket was closed after disconnection

def test_client_handler_handles_unexpected_disconnection(mock_socket, mock_parser):
    """Test that ClientHandler handles unexpected ConnectionResetError."""
    mock_socket.recv.side_effect = ConnectionResetError  # Simulate abrupt client disconnection

    handler = ClientHandler(mock_socket, ("127.0.0.1", 12345))
    handler.run()  # Run the handler

    mock_socket.close.assert_called_once()  # Ensure socket was closed properly

def test_client_handler_stops_on_exit_command(mock_socket, mock_parser):
    """Test that ClientHandler stops execution when receiving 'exit'."""
    mock_socket.recv.side_effect = [b"exit\n"]  # Simulate exit command

    handler = ClientHandler(mock_socket, ("127.0.0.1", 12345))
    handler.run()  # Run the handler

    mock_parser.parse.assert_called_with("exit\n")  # Ensure parser was called
    expected_response = str(Response("Ok", result="Response for exit")) + "\n"
    mock_socket.send.assert_called_with(expected_response.encode("utf-8"))  # Ensure response was sent
    mock_socket.close.assert_called_once()  # Ensure socket was closed after "exit"

def test_client_handler_ignores_empty_messages(mock_socket, mock_parser):
    """Test that ClientHandler ignores empty messages and does not crash."""
    mock_socket.recv.side_effect = [b"\n", b"exit\n"]  # Simulate empty input then exit

    handler = ClientHandler(mock_socket, ("127.0.0.1", 12345))
    handler.run()  # Run the handler

    mock_parser.parse.assert_called_with("exit\n")  # Ensure parser was called for 'exit'
    expected_response = str(Response("Ok", result="Response for exit")) + "\n"
    mock_socket.send.assert_called_with(expected_response.encode("utf-8"))  # Ensure response was sent
    mock_socket.close.assert_called_once()  # Ensure socket was closed properly

