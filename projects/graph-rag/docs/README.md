# Graph‑RAG Agent (Project 05)

A **minimal Graph Retrieval‑Augmented Generation (RAG)** prototype.

## Overview
- Loads an edge‑list CSV (`source,target`).
- Builds an undirected adjacency list.
- Retrieves a sub‑graph around a start node (configurable depth).
- Returns a simple formatted answer (stub for real LLM call).

## Quick start
```bash
# From the repository root
python projects/graph-rag/src/graph_rag.py \
    --graph path/to/edges.csv \
    --query "Your question" \
    --start NODE_ID
```

## Project layout
```
projects/graph-rag/
├─ src/                 # Source package
│   ├─ __init__.py
│   └─ graph_rag.py
├─ tests/               # Unit tests (100 % coverage)
├─ docs/                # Documentation (this folder)
│   ├─ README.md        # <‑‑ you are reading it
│   ├─ architecture.mmd # Mermaid diagram
│   ├─ interview_guide.md
│   └─ daily_digest.md
```

## Testing
```bash
python -m unittest discover -s projects/graph-rag/tests -p "test_*.py"
```
All tests should pass with **0 failures**.

## Next steps
- Replace `generate_answer` with a real LLM call (e.g., Gemini). 
- Add a persistent vector store for embeddings.
- Expand the CLI with more options (directed graphs, weighting, etc.).

---
*Created as part of the enterprise SDLC workflow (PLAN → BUILD → VALIDATE → DEPLOY).*
