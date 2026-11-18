# RAGBIT AIRA

A learning project (course lecture follow-along) for building a RAG
(Retrieval-Augmented Generation) pipeline: extract text from PDFs, embed it
into a vector database, and (eventually) answer questions about it with an
LLM.

This is a `uv` workspace with two packages, `backend` and `frontend`.
Right now all the working code lives in `backend`; `frontend` is still the
empty scaffold `uv init --package` generated.

## Setup

1. Install dependencies for every package in the workspace:

   ```bash
   uv sync --all-packages
   ```

2. Copy `.env.example` to `.env` and fill in your API keys:

   ```bash
   cp .env.example .env
   ```

   - `COHERE_API_KEY` — used by `data_models.py` to call Cohere's
     `embed-multilingual-v3.0` embedding model.
   - `NVIDIA_API` — reserved for the future question-answering step
     (`rag.py`), not used yet.

## Pipeline (how the scripts depend on each other)

```
backend/src/data/*.pdf
        │
        ▼  pdfs_to_text.py
backend/src/data/*.txt
        │
        ▼  ingestion.py  (uses data_models.py's Article + embedding model)
backend/src/knowledge_base/   (LanceDB vector database)
        │
        ▼  rag.py  (planned — not written yet)
     an answer
```

- **[pdfs_to_text.py](backend/src/pdfs_to_text.py)** — Stage 1. Reads every
  PDF in `DATA_PATH`, extracts its text with `pypdf`, and writes a matching
  `.txt` file next to it. Run with:

  ```bash
  uv run pdfs_to_text.py
  ```

  (run from `backend/src/`, where this file lives, or pass its path to
  `uv run` from elsewhere in the repo)

- **[backend/constants.py](backend/src/backend/constants.py)** — Shared
  path constants (`DATA_PATH`, `VECTOR_DATABASE_PATH`) so every script
  points at the same folders instead of hardcoding paths.

- **[backend/data_models.py](backend/src/backend/data_models.py)** — The
  shared data shapes. `Article` describes one row of the vector database
  (one per source document); it also sets up the Cohere embedding model
  that LanceDB calls automatically when rows are added. `Prompt` and
  `RagResponse` (request/response shapes for the Q&A step) are planned for
  `rag.py` but not written yet.

- **[backend/ingestion.py](backend/src/backend/ingestion.py)** — Stage 2.
  Reads every `.txt` file produced by `pdfs_to_text.py`, embeds its content,
  and writes it into the LanceDB database at `VECTOR_DATABASE_PATH`. This
  is the one-time (or re-run-when-docs-change) job that builds the
  database the (future) `rag.py` will search. Run with:

  ```bash
  uv run ingestion.py
  ```

  (run from `backend/src/backend/`, where this file lives, or pass its
  path to `uv run` from elsewhere in the repo)

- **`backend/src/explorations.ipynb`** — Scratch notebook for trying things
  out interactively (e.g. querying the vector database) outside the
  pipeline scripts above.

- **`rag.py`** (not written yet) — will load the vector database from
  `VECTOR_DATABASE_PATH` and use an LLM to answer questions (`Prompt` in →
  `RagResponse` out), using the embedded documents as context.

### Known issue

`extract_text_from_pdf()` in `pdfs_to_text.py` currently ignores the `path`
argument it's given and always reads `data/Netherland_Dwarf_rabbit.pdf`.
As a result, every generated `.txt` file currently contains the same
Netherland Dwarf rabbit text rather than its own PDF's content. See the
comment above that function for the one-line fix.

## Project setup history

This workspace was created with:

```bash
uv init --no-package python 3.13
uv init --package frontend
uv init --package backend
uv sync --all-packages
```
