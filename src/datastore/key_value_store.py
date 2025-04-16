from typing import Dict, Optional
from threading import RLock, local
from src.datastore.kv_store_interface import KeyValueStoreInterface

class KeyValueStore(KeyValueStoreInterface):
    def __init__(self) -> None:
        self._store: Dict[str, str] = {}
        self._lock = RLock()
        self._local = local()

    @property
    def transactions(self) -> list[Dict[str, Optional[str]]]:
        if not hasattr(self._local, "transactions"):
            self._local.transactions = []
        return self._local.transactions

    def put(self, key: str, value: str) -> None:
        with self._lock:
            if self.transactions:
                self.transactions[-1][key] = value
            else:
                self._store[key] = value

    def get(self, key: str) -> Optional[str]:
        with self._lock:
            for txn in reversed(self.transactions):
                if key in txn:
                    return txn[key]
            return self._store.get(key)

    def delete(self, key: str) -> bool:
        with self._lock:
            if self.transactions:
                if key in self._store or any(key in txn for txn in self.transactions):
                    self.transactions[-1][key] = None
                    return True
                return False
            return self._store.pop(key, None) is not None

    def start(self) -> None:
        with self._lock:
            self.transactions.append({})

    def commit(self) -> None:
        with self._lock:
            if not self.transactions:
                raise RuntimeError("No active transaction to commit.")

            txn = self.transactions.pop()

            if self.transactions:
                self.transactions[-1].update(txn)
            else:
                for key, value in txn.items():
                    if value is None:
                        self._store.pop(key, None)
                    else:
                        self._store[key] = value

    def rollback(self) -> None:
        with self._lock:
            if not self.transactions:
                raise RuntimeError("No active transaction to rollback.")
            self.transactions.pop()

