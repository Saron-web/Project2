from redis_cache import get_clean_data
from cosmos_db import get_cosmos_data
import json
import os

def load_clean_data():
    data = get_clean_data()
    if data:
        return data
    cosmos = get_cosmos_data()
    if cosmos:
        return cosmos
    if os.path.exists("clean_data.json"):
        with open("clean_data.json") as f:
            return json.load(f)
    return []
