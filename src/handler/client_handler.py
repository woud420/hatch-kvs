import socket
import threading

from datetime import datetime
from typing import Optional, Tuple

from src.handler.parser import CommandParser

class ClientHandler(threading.Thread):
    def __init__(self, client_socket: socket.socket, client_address: Tuple[str, int]) -> None:
        super().__init__()
        self.client_socket: socket.socket = client_socket
        self.client_address: Tuple[str, int] = client_address

    def run(self) -> None:
        print(f"[+] New connection from {self.client_address}")

        parser = CommandParser()
        while True:
            try:
                data: Optional[str] = self.client_socket.recv(1024).decode("utf-8")
                if not data:
                    break # client gone

                print(f"[{self.client_address}] Received: {data.strip()}")

                response: str = parser.parse(data) + "\n" # just so it's easier to read
                self.client_socket.send(response.encode("utf-8"))

                if data.strip().lower() == "exit":
                    break  # bye bye bye
            except ConnectionResetError:
                break  # woops, just assume connection closed

        print(f"[-] Connection closed: {self.client_address}")
        self.client_socket.close()

