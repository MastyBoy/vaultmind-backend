from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time

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

mock_memory = []
mock_logs = []
mock_feedback = []

@app.post("/execute")
async def execute_command(cmd: Command):
    result = f"VaultMind executed: {cmd.input}"
    mock_memory.append({"timestamp": time.time(), "command": cmd.input, "result": result})
    return {"result": result}

@app.get("/memory")
def get_memory():
    return mock_memory

@app.post("/log")
def log_event(entry: LogEvent):
    mock_logs.append({"timestamp": time.time(), "source": entry.source, "event": entry.event, "data": entry.data})
    return {"status": "logged"}

@app.get("/log")
def get_logs():
    return mock_logs

@app.post("/feedback")
def collect_feedback(entry: Feedback):
    mock_feedback.append({
        "timestamp": time.time(),
        "command": entry.command,
        "result": entry.result,
        "rating": entry.rating,
        "note": entry.note
    })
    return {"status": "feedback recorded"}

@app.get("/feedback")
def get_feedback():
    return mock_feedback
