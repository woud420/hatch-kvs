import time
import threading
import pytest

from src.datastore.key_value_store import KeyValueStore

def test_put_get():
    """Test storing and retrieving values."""
    store = KeyValueStore()
    store.put("key1", "value1")
    assert store.get("key1") == "value1"

def test_get_non_existent_key():
    """Test retrieving a non-existent key returns None."""
    store = KeyValueStore()
    assert store.get("missing_key") is None

def test_delete_existing_key():
    """Test deleting an existing key returns True and removes it."""
    store = KeyValueStore()
    store.put("key1", "value1")
    assert store.delete("key1") is True
    assert store.get("key1") is None

def test_delete_non_existent_key():
    """Test deleting a non-existent key returns False."""
    store = KeyValueStore()
    assert store.delete("missing_key") is False

def test_start_transaction():
    """Test that starting a transaction creates an isolated storage layer."""
    store = KeyValueStore()
    store.start()
    store.put("temp_key", "temp_value")
    assert store.get("temp_key") == "temp_value"
    assert store.transactions  # Ensure transaction is active
    assert "temp_key" not in store._store  # Key should not be in main store yet

def test_commit_transaction():
    """Test committing a transaction applies changes to the main store."""
    store = KeyValueStore()
    store.start()
    store.put("temp_key", "temp_value")
    store.commit()
    assert store.get("temp_key") == "temp_value"
    assert not store.transactions  # Transaction stack should be empty

def test_rollback_transaction():
    """Test rolling back a transaction discards changes."""
    store = KeyValueStore()
    store.put("key1", "original_value")
    store.start()
    store.put("key1", "new_value")  # Modify key inside transaction
    store.rollback()
    assert store.get("key1") == "original_value"  # Should revert to original value

def test_commit_with_delete():
    """Test committing a transaction with a delete operation."""
    store = KeyValueStore()
    store.put("key1", "value1")
    store.start()
    store.delete("key1")
    store.commit()
    assert store.get("key1") is None  # Ensure key is deleted after commit

def test_rollback_with_delete():
    """Test rolling back a delete operation restores the original key."""
    store = KeyValueStore()
    store.put("key1", "value1")
    store.start()
    store.delete("key1")
    store.rollback()
    assert store.get("key1") == "value1"  # Should restore the key

def test_nested_transactions():
    """Test nested transactions apply changes correctly."""
    store = KeyValueStore()
    store.put("key1", "value1")

    store.start()
    store.put("key1", "temp_value")

    store.start()
    store.put("key1", "nested_value")
    store.commit()  # Commit only inner transaction

    assert store.get("key1") == "nested_value"

    store.rollback()  # Rollback outer transaction
    assert store.get("key1") == "value1"  # Should revert to original

def test_commit_without_transaction():
    """Test committing without an active transaction raises an error."""
    store = KeyValueStore()
    with pytest.raises(RuntimeError, match="No active transaction to commit."):
        store.commit()

def test_rollback_without_transaction():
    """Test rolling back without an active transaction raises an error."""
    store = KeyValueStore()
    with pytest.raises(RuntimeError, match="No active transaction to rollback."):
        store.rollback()

def test_concurrent_transactions():
    """Test thread safety by running multiple transactions in parallel."""
    store = KeyValueStore()

    def worker():
        store.start()
        store.put("shared_key", "thread_value")
        store.commit()

    threads = [threading.Thread(target=worker) for _ in range(5)]

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    assert store.get("shared_key") == "thread_value"  # Ensure last commit wins

def test_concurrent_isolated_transactions():
    store = KeyValueStore()
    results = []

    def worker(thread_id, key, value, commit=True, delay=0):
        store.start()
        store.put(key, value)
        time.sleep(delay)  # simulate some work
        if not commit:
            store.rollback()
            results.append((thread_id, store.get(key)))  # should be None
        else:
            store.commit()
            results.append((thread_id, store.get(key)))  # should be the value

    threads = [
        threading.Thread(target=worker, args=(1, "k1", "v1", True)),
        threading.Thread(target=worker, args=(2, "k2", "v2", False)),
        threading.Thread(target=worker, args=(3, "k3", "v3", True)),
        threading.Thread(target=worker, args=(4, "k1", "v4", True, 0.1)),  # overwrite after delay
    ]

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Ensure correct committed state
    assert store.get("k1") == "v4"  # last committed value
    assert store.get("k2") is None  # rolled back
    assert store.get("k3") == "v3"  # committed

    # Ensure each thread saw the expected state at the end
    for tid, observed in results:
        if tid == 2:
            assert observed is None
        elif tid == 1:
            assert observed == "v1" or observed == "v4"  # depends on timing
        elif tid == 3:
            assert observed == "v3"
        elif tid == 4:
            assert observed == "v4"

