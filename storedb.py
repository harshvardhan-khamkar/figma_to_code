from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

client = MongoClient(MONGO_URI)
db = client["figma_to_code"]
collection = db["figma_files"]

collection.create_index(
    [("figma_url", 1), ("framework", 1)],
    unique=True
)


def save_figma_file(figma_url: str, figma_json: dict, layout: dict, framework: str):
    collection.update_one(
        {"figma_url": figma_url, "framework": framework},
        {
            "$set": {
                "figma_url": figma_url,
                "framework": framework,
                "figma_json": figma_json,
                "parsed_layout": layout,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )


def get_cached_figma(figma_url: str, framework: str):
    return collection.find_one(
        {"figma_url": figma_url, "framework": framework},
        {"_id": 0}
    )
