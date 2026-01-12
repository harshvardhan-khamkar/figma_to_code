import os
import requests
import re
import time
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

FIGMA_TOKEN = os.getenv("FIGMA_TOKEN")

if not FIGMA_TOKEN:
    raise RuntimeError("FIGMA_TOKEN not set")

HEADERS = {
    "X-Figma-Token": FIGMA_TOKEN
}


def extract_file_key(figma_url: str) -> str:
    match = re.search(r"/(file|design|make)/([a-zA-Z0-9]+)", figma_url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid Figma URL")
    return match.group(2)


def get_figma_file(figma_url: str) -> dict:
    file_key = extract_file_key(figma_url)
    time.sleep(1)

    url = f"https://api.figma.com/v1/files/{file_key}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()
