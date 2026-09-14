import json
from pathlib import Path


METADATA_FILE = Path("../index_metadata.json")


def load_metadata():
    
    if not METADATA_FILE.exists():
        return {
            "indexed": False,
            "repo": None,
            "branch": None,
            "commit": None,
            "files": {}
        }

    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)

    except Exception:
        return {
            "indexed": False,
            "repo": None,
            "branch": None,
            "commit": None,
            "files": {}
        }


def save_metadata(metadata):
    
    with open(METADATA_FILE, "w", encoding="utf-8") as file:
        json.dump(metadata, file,indent=2)