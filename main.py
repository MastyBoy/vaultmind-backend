from fastapi import FastAPI, Query
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time, json, os, subprocess
from typing import List, Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
def get_memory(limit: Optional[int] = None, offset: int = 0, search: Optional[str] = None):
    if not os.path.exists("vaultmind_memory.json"):
        return []
    with open("vaultmind_memory.json", "r") as f:
        lines = [json.loads(line.strip()) for line in f if line.strip()]
    if search:
        lines = [entry for entry in lines if search.lower() in entry["command"].lower() or search.lower() in entry["result"].lower()]
    return lines[offset:(offset + limit) if limit else None]

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
def get_feedback(limit: Optional[int] = None, offset: int = 0, rating: Optional[int] = None, search: Optional[str] = None):
    if not os.path.exists("vaultmind_feedback.json"):
        return []
    with open("vaultmind_feedback.json", "r") as f:
        lines = [json.loads(line.strip()) for line in f if line.strip()]
    if rating is not None:
        lines = [entry for entry in lines if entry.get("rating") == rating]
    if search:
        lines = [entry for entry in lines if search.lower() in entry["command"].lower() or search.lower() in entry["result"].lower() or search.lower() in entry["note"].lower()]
    return lines[offset:(offset + limit) if limit else None]

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
def get_logs(limit: Optional[int] = None, offset: int = 0, source: Optional[str] = None, search: Optional[str] = None):
    if not os.path.exists("vaultmind_log.json"):
        return []
    with open("vaultmind_log.json", "r") as f:
        lines = [json.loads(line.strip()) for line in f if line.strip()]
    if source:
        lines = [entry for entry in lines if entry.get("source") == source]
    if search:
        lines = [entry for entry in lines if search.lower() in entry["event"].lower() or search.lower() in json.dumps(entry.get("data", {})).lower()]
    return lines[offset:(offset + limit) if limit else None]
