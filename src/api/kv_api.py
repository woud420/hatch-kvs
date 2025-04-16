import threading

from typing import Optional

from src.datastore.kv_store_interface import KeyValueStoreInterface
from src.datastore.key_value_store import KeyValueStore

from src.model.response import Response

class KeyValueAPI:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance.store: KeyValueStoreInterface = KeyValueStore()
        return cls._instance

    def delete(self, key: str) -> Response:
        try:
            result = self.store.delete(key)
            return Response("Ok" if result else "Error", str(result))
        except Exception as e:
            return Response("Error", mesg=str(e))

    def get(self, key: str) -> Response:
        try:
            result = self.store.get(key)
            return Response("Ok", result if result else f"{key} was not found.")
        except Exception as e:
            return Response("Error", mesg=str(e))

    def put(self, key: str, value: str) -> Response:
        try:
            self.store.put(key, value)
            return Response("Ok")
        except Exception as e:
            return Response("Error", mesg=str(e))

    def start(self) -> Response:
        try:
            self.store.start()
            return Response("Ok")
        except Exception as e:
            return Response("Error", mesg=str(e))

    def commit(self) -> Response:
        try:
            self.store.commit()
            return Response("Ok")
        except Exception as e:
            return Response("Error", mesg=str(e))

    def rollback(self) -> Response:
        try:
            self.store.rollback()
            return Response("Ok")
        except Exception as e:
            return Response("Error", mesg=str(e))

