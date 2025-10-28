import json
import os
import config

def load_memory():
    if os.path.exists(config.MEMORY_FILE):
        with open(config.MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "thoughts": [],
        "emotions": [],
        "skills": [],
        "concepts": [],
        "projects": [],
        "history": [],
        "stats": {"interactions": 0, "essays_generated": 0, "version": config.VERSION},
    }

def save_memory(memory):
    with open(config.MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)
