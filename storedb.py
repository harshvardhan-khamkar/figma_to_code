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


def save_figma_json(figma_url: str, figma_json: dict, framework: str):
    collection.update_one(
        {"figma_url": figma_url, "framework": framework},
        {
            "$set": {
                "figma_url": figma_url,
                "framework": framework,
                "figma_json": figma_json,
                "updated_at": datetime.utcnow()
            }
        },
        upsert=True
    )


def update_parsed_layout(figma_url: str, framework: str, layout: dict):
    collection.update_one(
        {"figma_url": figma_url, "framework": framework},
        {
            "$set": {
                "parsed_layout": layout,
                "parsed_at": datetime.utcnow()
            }
        }
    )


def get_cached_figma(figma_url: str, framework: str):
    return collection.find_one(
        {"figma_url": figma_url, "framework": framework},
        {"_id": 0}
    )
