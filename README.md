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
| `training/` | RAFT dataset + fine-tuning (W3) |
| `evaluation/` | Baseline vs RAG vs GRAFT comparison (W5) |
| `ui/` | Multi-turn chat interface (W6) |

## Run

```bash
pip install -r requirements.txt
pytest
uvicorn api.main:app --reload
```

Then `POST /chat` with `{"session_id": "demo", "message": "My son is 9 years old. Is dental covered?"}`.

## Roadmap

- W1-W2: knowledge graph + vector index (skeleton done)
- W3: RAFT fine-tuning on real + synthetic data
- W4: memory manager hardening
- W5: comparative evaluation
- W6: prototype UI + poster
