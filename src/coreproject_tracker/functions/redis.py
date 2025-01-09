import json
import time


# Function to set a field with TTL
def hset_with_ttl(redis, hash_key, field, value, ttl_seconds):
    expiration = time.time() + ttl_seconds
    redis.hset(hash_key, field, json.dumps({"value": value, "expires_at": expiration}))


# Function to get a field and check expiration
def hget_with_ttl(redis, hash_key, field):
    data = redis.hget(hash_key, field)
    if data:
        record = json.loads(data)
        if time.time() < record["expires_at"]:
            return record["value"]
        else:
            redis.hdel(hash_key, field)
    return None
