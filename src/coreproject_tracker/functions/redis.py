import json
import time

from coreproject_tracker.constants import HASH_EXPIRE_TIME
from coreproject_tracker.singletons import RedisConnectionManager


def hset_with_ttl(hash_key, field, value, ttl_seconds):
    r = RedisConnectionManager.get_client()

    expiration = time.time() + ttl_seconds
    r.hset(hash_key, field, json.dumps({"value": value, "expires_at": expiration}))
    r.expire(hash_key, HASH_EXPIRE_TIME)


def hget_all_with_ttl(hash_key):
    r = RedisConnectionManager.get_client()

    # Retrieve all fields and their values from the hash
    data = r.hgetall(hash_key)
    if not data:
        return None  # Return None if the hash doesn't exist or is empty

    # Update the ttl again
    r.expire(hash_key, HASH_EXPIRE_TIME)
    valid_fields = {}

    # Iterate over each field-value pair in the hash
    for field, value in data.items():
        record = json.loads(value)  # Decode bytes and parse JSON
        if time.time() < record["expires_at"]:  # Check if the field has expired
            valid_fields[field] = record["value"]  # Add valid field to result
        else:
            # Optionally delete expired field
            r.hdel(hash_key, field)

    if not valid_fields:
        r.delete(hash_key)
        return None

    return valid_fields
