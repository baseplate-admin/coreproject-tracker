import time

from coreproject_tracker.singletons.redis import RedisConnectionManager


def list_with_ttl_add(list_key, item, ttl_seconds):
    """
    Add an item to the list with a TTL at the application level.
    TTL is managed using a sorted set where the expiration time is stored as the score.
    """
    r = RedisConnectionManager.get_client()
    # Calculate expiration time (current time + TTL)
    expiration_time = time.time() + ttl_seconds
    # Add item to list (this can be done with LPUSH, RPUSH, etc.)
    r.rpush(list_key, item)
    # Store the expiration time in a sorted set to track each item’s TTL
    r.zadd(f"{list_key}:ttl", {item: expiration_time})


def list_with_ttl_get(list_key):
    """
    Retrieve non-expired items from the list and remove expired items.
    """
    r = RedisConnectionManager.get_client()
    current_time = time.time()
    # Retrieve all items from the list
    items = r.lrange(list_key, 0, -1)
    valid_items = []

    # Check expiration for each item in the list using the sorted set
    for item in items:
        expiration_time = r.zscore(f"{list_key}:ttl", item)

        if expiration_time and expiration_time > current_time:
            valid_items.append(item)
        else:
            # Remove expired item from the list and TTL tracking sorted set
            r.lrem(list_key, 0, item)  # Remove item from the list
            r.zrem(f"{list_key}:ttl", item)  # Remove item from the sorted set

    return valid_items
