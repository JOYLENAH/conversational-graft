"""FastAPI app: POST /chat keeps one memory tracker per session id."""
from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from graft.memory import MemoryTracker
from graft.pipeline import GraftPipeline

app = FastAPI(title="Conversational GRAFT")
pipeline = GraftPipeline.from_policy_file()
sessions: dict[str, MemoryTracker] = {}


class ChatRequest(BaseModel):
    session_id: str
    message: str


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
