"""
Unit tests for IdempotencyStore class.
"""
from datetime import datetime, timedelta, timezone

from app.common.cache.idempotency import IdempotencyStore


def test_idempotency_store_initialization():
    """Test IdempotencyStore initializes correctly"""
    store = IdempotencyStore()
    assert store.ttl_hours == 24
    assert store.size() == 0


def test_idempotency_store_custom_ttl():
    """Test IdempotencyStore with custom TTL"""
    store = IdempotencyStore(ttl_hours=48)
    assert store.ttl_hours == 48


def test_store_and_check_key():
    """Test storing and checking idempotency key"""
    store = IdempotencyStore()
    key = "test-key-123"
    user_id = 1
    response = {"message": "Test response"}

    # Store key
    store.store(key, user_id, response)
    assert store.size() == 1

    # Check key returns stored response
    cached = store.check(key, user_id)
    assert cached == response


def test_check_nonexistent_key():
    """Test checking non-existent key returns None"""
    store = IdempotencyStore()
    cached = store.check("nonexistent-key", 1)
    assert cached is None


def test_user_scoped_keys():
    """Test that keys are scoped per user"""
    store = IdempotencyStore()
    key = "shared-key"
    user1_id = 1
    user2_id = 2
    response1 = {"message": "User 1 response"}
    response2 = {"message": "User 2 response"}

    # Store same key for different users
    store.store(key, user1_id, response1)
    store.store(key, user2_id, response2)

    # Each user gets their own response
    assert store.check(key, user1_id) == response1
    assert store.check(key, user2_id) == response2


def test_wrong_user_returns_none():
    """Test that checking key with wrong user_id returns None"""
    store = IdempotencyStore()
    key = "test-key"
    user_id = 1
    wrong_user_id = 2
    response = {"message": "Test response"}

    store.store(key, user_id, response)

    # Correct user gets response
    assert store.check(key, user_id) == response

    # Wrong user gets None
    assert store.check(key, wrong_user_id) is None


def test_clear_store():
    """Test clearing the store"""
    store = IdempotencyStore()
    store.store("key1", 1, {"msg": "response1"})
    store.store("key2", 2, {"msg": "response2"})

    assert store.size() == 2

    store.clear()

    assert store.size() == 0
    assert store.check("key1", 1) is None
    assert store.check("key2", 2) is None


def test_expired_key_cleanup():
    """Test that expired keys are cleaned up"""
    store = IdempotencyStore(ttl_hours=0)  # 0 hour TTL for testing
    key = "test-key"
    user_id = 1
    response = {"message": "Test response"}

    store.store(key, user_id, response)
    assert store.size() == 1

    # Manually expire the key by modifying stored timestamp (using scoped key)
    old_timestamp = datetime.now(timezone.utc) - timedelta(hours=1)
    scoped_key = f"{user_id}:{key}"
    store._store[scoped_key] = (old_timestamp, response, user_id)

    # Check should trigger cleanup and return None
    cached = store.check(key, user_id)
    assert cached is None


def test_lazy_cleanup_removes_multiple_expired_keys():
    """Test that lazy cleanup removes all expired keys"""
    store = IdempotencyStore(ttl_hours=1)

    # Add some keys
    store.store("key1", 1, {"msg": "response1"})
    store.store("key2", 2, {"msg": "response2"})
    store.store("key3", 3, {"msg": "response3"})

    assert store.size() == 3

    # Manually expire two keys (using scoped keys)
    old_timestamp = datetime.now(timezone.utc) - timedelta(hours=2)
    store._store["1:key1"] = (old_timestamp, {"msg": "response1"}, 1)
    store._store["2:key2"] = (old_timestamp, {"msg": "response2"}, 2)

    # Trigger cleanup by checking any key
    store.check("key3", 3)

    # Only unexpired key should remain
    assert store.size() == 1
    assert store.check("key3", 3) is not None
    assert store.check("key1", 1) is None
    assert store.check("key2", 2) is None


def test_multiple_stores_and_checks():
    """Test multiple store and check operations"""
    store = IdempotencyStore()

    for i in range(10):
        key = f"key-{i}"
        user_id = i
        response = {"message": f"Response {i}"}
        store.store(key, user_id, response)

    assert store.size() == 10

    for i in range(10):
        key = f"key-{i}"
        user_id = i
        cached = store.check(key, user_id)
        assert cached == {"message": f"Response {i}"}


def test_overwrite_existing_key():
    """Test that storing same key overwrites previous value"""
    store = IdempotencyStore()
    key = "test-key"
    user_id = 1
    response1 = {"message": "First response"}
    response2 = {"message": "Second response"}

    store.store(key, user_id, response1)
    assert store.check(key, user_id) == response1

    # Store again with same key (same user)
    store.store(key, user_id, response2)
    assert store.check(key, user_id) == response2
    assert store.size() == 1  # Still only one entry


def test_store_complex_response():
    """Test storing complex response objects"""
    store = IdempotencyStore()
    key = "test-key"
    user_id = 1
    complex_response = {
        "message": "Success",
        "data": {
            "items": [1, 2, 3],
            "count": 3,
            "nested": {"key": "value"}
        },
        "status": "ok"
    }

    store.store(key, user_id, complex_response)
    cached = store.check(key, user_id)

    assert cached == complex_response
    assert cached["data"]["items"] == [1, 2, 3]
    assert cached["data"]["nested"]["key"] == "value"
