"""FastAPI app.

- GET  /            the chat interface (ui/index.html)
- POST /chat        one message in, answer + citations + evidence + memory + scores out
- DELETE /session/  forget a conversation
"""
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from graft.memory import MemoryTracker
from graft.pipeline import GraftPipeline

UI_FILE = Path(__file__).resolve().parent.parent / "ui" / "index.html"

app = FastAPI(title="Conversational GRAFT")
pipeline = GraftPipeline.from_policy_file()
sessions: dict[str, MemoryTracker] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(UI_FILE, media_type="text/html")


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "policy": pipeline.graph.policy_name}


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    memory = sessions.setdefault(req.session_id, MemoryTracker())
    return pipeline.chat(memory, req.message)


@app.delete("/session/{session_id}")
def reset(session_id: str) -> dict:
    sessions.pop(session_id, None)
    return {"reset": session_id}
