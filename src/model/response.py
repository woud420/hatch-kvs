import json
from typing import Optional

class Response:
    def __init__(self, status: str, result: Optional[str] = None, mesg: Optional[str] = None):
        self.status = status
        self.result = result
        self.mesg = mesg

    def __str__(self) -> str:
        response = {"status": self.status}
        if self.result is not None:
            response["result"] = self.result
        if self.mesg is not None:
            response["mesg"] = self.mesg
        return json.dumps(response)

