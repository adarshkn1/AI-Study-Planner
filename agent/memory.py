import json
import os

MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {
            "completed_days": [],
            "missed_days": []
        }

    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

def mark_day_completed(date):
    memory = load_memory()
    if date not in memory["completed_days"]:
        memory["completed_days"].append(date)
    save_memory(memory)

def mark_day_missed(date):
    memory = load_memory()
    if date not in memory["missed_days"]:
        memory["missed_days"].append(date)
    save_memory(memory)
