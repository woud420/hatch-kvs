from abc import ABC, abstractmethod
from typing import Dict, Optional

class KeyValueStoreInterface(ABC):
    @abstractmethod
    def put(self, key: str, value: str) -> None:
        """Stores a key-value pair in the store."""
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """Retrieves the value for a given key, or None if the key does not exist."""
        pass

    @abstractmethod
    def delete(self, key: str) -> None:
        """Removes a key from the store."""
        pass

    @abstractmethod
    def start(self) -> None:
        """Starts a new transaction."""
        pass

    @abstractmethod
    def commit(self) -> None:
        """Commits the active transaction."""
        pass

    @abstractmethod
    def rollback(self) -> None:
        """Rolls back the active transaction."""
        pass

