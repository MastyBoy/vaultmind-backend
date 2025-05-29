from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import time, json, os

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

# /execute (simulated)
@app.post("/execute")
async def execute_command(cmd: Command):
    result = f"VaultMind executed: {cmd.input}"
    log_to_memory(cmd.input, result)
    print(result)
    return {"result": result}

# /memory
@app.get("/memory")
def get_memory():
    if not os.path.exists("vaultmind_memory.json"):
        return []
    with open("vaultmind_memory.json", "r") as f:
        lines = f.readlines()
        return [json.loads(line.strip()) for line in lines]

import subprocess

@app.post("/execute")
async def execute_command(cmd: Command):
    try:
        result = subprocess.run(cmd.input, shell=True, capture_output=True, text=True, timeout=10)
        output = result.stdout if result.stdout else result.stderr
    except Exception as e:
        output = f"Error: {str(e)}"
    log_to_memory(cmd.input, output)
    return {"result": output}

# /feedback
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

@app.get("/log")
def get_logs():
    if not os.path.exists("vaultmind_log.json"):
        return []
    with open("vaultmind_log.json", "r") as f:
        return [json.loads(line.strip()) for line in f]



