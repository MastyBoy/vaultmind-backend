from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time, json, os, subprocess

app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Schemas
class Command(BaseModel):
    input: str

class LogEvent(BaseModel):
    source: str
    event: str
    data: dict

class Feedback(BaseModel):
    command: str
    result: str
    rating: int
    note: str = ""

# Memory logger
def log_to_memory(command, result):
    entry = {
        "timestamp": time.time(),
        "command": command,
        "result": result
    }
    with open("vaultmind_memory.json", "a") as f:
        f.write(json.dumps(entry) + "\n")

@app.post("/execute")
async def execute_command(cmd: Command):
    try:
        result = subprocess.run(cmd.input, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else result.stderr
    except Exception as e:
        output = f"Error: {str(e)}"
    log_to_memory(cmd.input, output)
    return {"result": output}

@app.get("/memory")
def get_memory():
    if not os.path.exists("vaultmind_memory.json"):
        return []
    with open("vaultmind_memory.json", "r") as f:
        return [json.loads(line.strip()) for line in f]

@app.post("/feedback")
def collect_feedback(entry: Feedback):
    log = {
        "timestamp": time.time(),
        "command": entry.command,
        "result": entry.result,
        "rating": entry.rating,
        "note": entry.note
    }
    with open("vaultmind_feedback.json", "a") as f:
        f.write(json.dumps(log) + "\n")
    return {"status": "feedback recorded"}

@app.get("/feedback")
def get_feedback(
    rating: int = Query(None),
    min_rating: int = Query(None),
    max_rating: int = Query(None),
    note_contains: str = Query(None),
    type: str = Query(None),
    limit: int = Query(None)
):
    if not os.path.exists("vaultmind_feedback.json"):
        return []
    with open("vaultmind_feedback.json", "r") as f:
        entries = [json.loads(line.strip()) for line in f]

    filtered = []
    for entry in entries:
        if rating is not None and entry["rating"] != rating:
            continue
        if min_rating is not None and entry["rating"] < min_rating:
            continue
        if max_rating is not None and entry["rating"] > max_rating:
            continue
        if note_contains and note_contains.lower() not in entry["note"].lower():
            continue
        if type and entry.get("type") != type:
            continue
        filtered.append(entry)
        if limit and len(filtered) >= limit:
            break
    return filtered


@app.post("/log")
def log_event(entry: LogEvent):
    log = {
        "timestamp": time.time(),
        "source": entry.source,
        "event": entry.event,
        "data": entry.data
    }
    with open("vaultmind_log.json", "a") as f:
        f.write(json.dumps(log) + "\n")
    return {"status": "logged"}

@app.get("/log")
def get_logs():
    if not os.path.exists("vaultmind_log.json"):
        return []
    with open("vaultmind_log.json", "r") as f:
        return [json.loads(line.strip()) for line in f]

from collections import Counter

@app.get("/feedback_summary")
def feedback_summary():
    if not os.path.exists("vaultmind_feedback.json"):
        return {
            "total_entries": 0,
            "average_rating": 0,
            "rating_distribution": {},
            "top_keywords": []
        }

    with open("vaultmind_feedback.json", "r") as f:
        entries = [json.loads(line.strip()) for line in f]

    total = len(entries)
    if total == 0:
        return {
            "total_entries": 0,
            "average_rating": 0,
            "rating_distribution": {},
            "top_keywords": []
        }

    avg_rating = sum(e["rating"] for e in entries) / total
    distribution = Counter(e["rating"] for e in entries)

    all_words = " ".join(e["note"] for e in entries if e["note"]).lower().split()
    keywords = Counter(all_words).most_common(5)

    return {
        "total_entries": total,
        "average_rating": round(avg_rating, 2),
        "rating_distribution": dict(distribution),
        "top_keywords": [kw for kw, _ in keywords]
    }

