import json
import redis

r = redis.Redis(host="localhost", port=6379, db=0)

def save_clean_data(data):
    r.set("clean_data", json.dumps(data))

def get_clean_data():
    raw = r.get("clean_data")
    if raw:
        return json.loads(raw)
    return []
