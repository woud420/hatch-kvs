from typing import List
from src.api.kv_api import KeyValueAPI
from src.model.response import Response

class CommandParser:
    def __init__(self) -> None:
        self.api = KeyValueAPI()  # singleton

    def parse(self, command: str) -> str:
        """Parses the given command and executes the corresponding API method."""
        parts: List[str] = command.strip().split(" ", 2)
        if not parts or parts[0] == "":
            return str(Response("Error", mesg="Empty command. Available commands: PUT, GET, DEL, START, COMMIT, ROLLBACK"))

        cmd: str = parts[0].upper() # let's assume we don't care if put or PUT or pUt

        try:
            if cmd == "PUT":
                if len(parts) == 3:
                    key, value = parts[1], parts[2]
                    return str(self.api.put(key, value))
                return str(Response("Error", mesg="PUT requires two arguments. Usage: PUT <key> <value>"))

            elif cmd == "GET":
                if len(parts) == 2:
                    key = parts[1]
                    return str(self.api.get(key))
                return str(Response("Error", mesg="GET requires one argument. Usage: GET <key>"))

            elif cmd == "DEL":
                if len(parts) == 2:
                    key = parts[1]
                    return str(self.api.delete(key))
                return str(Response("Error", mesg="DEL requires one argument. Usage: DEL <key>"))

            elif cmd == "START":
                if len(parts) == 1:
                    return str(self.api.start())
                return str(Response("Error", mesg="START does not take arguments."))

            elif cmd == "COMMIT":
                if len(parts) == 1:
                    return str(self.api.commit())
                return str(Response("Error", mesg="COMMIT does not take arguments."))

            elif cmd == "ROLLBACK":
                if len(parts) == 1:
                    return str(self.api.rollback())
                return str(Response("Error", mesg="ROLLBACK does not take arguments."))

            else:
                return str(Response("Error", mesg=f"Unknown command '{cmd}'. Available commands: PUT, GET, DEL, START, COMMIT, ROLLBACK"))

        except Exception as e:
            return str(Response("Error", mesg=str(e)))

