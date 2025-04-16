import socket
import threading
import logging
from typing import Tuple
from src.handler.client_handler import ClientHandler

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class TCPServer:
    def __init__(self, host: str = "0.0.0.0", port: int = 4000, max_clients: int = 5) -> None:
        self.host: str = host
        self.port: int = port
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # reuse socket if needed
        self.max_clients = max_clients
        self.running = False

    def start(self) -> None:
        """Start the TCP server and handle incoming client connections."""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(self.max_clients)
            self.running = True
            logging.info(f"Server started on {self.host}:{self.port}")

            while self.running:
                try:
                    client_socket, client_address = self.server_socket.accept()
                    logging.info(f"New connection from {client_address}")
                    handler = ClientHandler(client_socket, client_address)
                    handler.start()
                except KeyboardInterrupt:
                    logging.info("Keyboard interrupt received. Shutting down server...")
                    self.stop()
                    break
                except Exception as e:
                    logging.error(f"Error accepting connection: {e}")

        except Exception as e:
            logging.error(f"Server error: {e}")
        finally:
            self.stop()

    def stop(self) -> None:
        """Stops the server and closes the socket."""
        self.running = False
        if self.server_socket:
            self.server_socket.close()
            logging.info("Server stopped.")

