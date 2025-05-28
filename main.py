from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS from any origin (for now)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Command(BaseModel):
    input: str

@app.post("/execute")
async def execute_command(cmd: Command):
    print(f"Executing: {cmd.input}")
    return {"result": f"VaultMind executed: {cmd.input}"}
