# Conversational GRAFT

Graph-Augmented Retrieval and Fine-Tuning for child health insurance advisory.
A conversational AI system that reduces hallucinations and context loss in multi-turn policy dialogues.

## Pipeline

```
User query + Session-State Memory (age, dependent status, prior turns)
        |
Policy Knowledge Graph  +  Hybrid retrieval over exact clause text
        |
Domain-adapted LLM (RAFT fine-tuned, distractor-resistant prompt)
        |
Grounded answer + policy citation + faithfulness / retention score
```

## Layout

| Folder | Purpose |
|---|---|
| `graft/memory.py` | Session-state tracker |
| `graft/graph.py` | Policy knowledge graph (NetworkX; Neo4j-ready interface) |
| `graft/retrieval.py` | Clause vector index (TF-IDF now; swap for embeddings/FAISS) |
| `graft/llm.py` | LLM interface, shared prompt builder, rule-based stand-in |
| `graft/pipeline.py` | Orchestration |
| `graft/metrics.py` | Faithfulness and constraint-retention proxies |
| `api/` | FastAPI `/chat` endpoint |
| `data/` | Policy data (sample file is synthetic; real policies use the same schema) |
| `tests/` | Automated tests (memory, grounding, API sessions) |
| `training/` | RAFT dataset + fine-tuning (planned, W3) |
| `evaluation/` | Baseline vs RAG vs GRAFT comparison (planned, W5) |
| `ui/` | Multi-turn chat interface (planned, W6) |

## Setup and run (Windows, VS Code)

Requires Python 3.10 or newer. Open the project folder (the one containing
`requirements.txt`) in VS Code, open a terminal with Ctrl + `, then:

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the tests (expect: 7 passed)
pytest

# 4. Start the server
uvicorn api.main:app --reload
```

If PowerShell blocks the activate script, run this once in the same terminal and retry:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
```

Each new terminal needs step 1's `.venv\Scripts\Activate.ps1` again (the prompt
should start with `(.venv)`).

## Try it

1. With the server running, open <http://127.0.0.1:8000/health>. It should return `{"status":"ok", ...}`.
2. Open <http://127.0.0.1:8000/docs>, click **POST /chat**, then **Try it out**.
3. Send messages using the same `session_id` so the memory carries across turns:

```json
{"session_id": "demo", "message": "My daughter is 20 and a full-time student"}
{"session_id": "demo", "message": "Is dental covered?"}
{"session_id": "demo", "message": "And the waiting period?"}
```

Each response contains the `answer`, the policy `citations`, the `memory_state`,
and the `scores` (faithfulness, constraint retention, latency). Stop the server
with Ctrl + C.

## Roadmap

- W1-W2: knowledge graph + vector index (skeleton done)
- W3: RAFT fine-tuning on real + synthetic data
- W4: memory manager hardening
- W5: comparative evaluation
- W6: prototype UI + poster
