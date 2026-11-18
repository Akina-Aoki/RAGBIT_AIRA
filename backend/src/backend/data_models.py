"""
This is the shared vocabulary of the whole project — the data shapes that
ingestion.py, rag.py and api.py pass around, defined once here so all three
agree.

Article describes what gets stored in the vector database (one row per
source document, built by ingestion.py).

Prompt describes what comes in from the user (api.py's request body).
RagResponse describes what goes out as the answer (rag_agent's output_type
in rag.py) — drafted here as a reasonable guess; compare against whatever
shape the lecture actually used.
"""

import os
from pydantic import BaseModel, Field
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from dotenv import load_dotenv

# Loads variables from a .env file (e.g. the Cohere API key) into the
# environment so the embedding model below can authenticate.
load_dotenv()

# Cohere's multilingual embedding model, wrapped so LanceDB can call it
# automatically whenever a row is added to a table that uses it (see
# content/embedding fields below).
embedding_model = get_registry().get("cohere").create(name="embed-multilingual-v3.0")

class Article(LanceModel):
    """
    One row of the "articles" table in the vector database — one per
    source document (e.g. one rabbit-breed .txt file).

    doc_id/filepath/filename: identify which source file this row came from.
    content: the raw extracted text. Marked as the embedding model's
        SourceField, meaning "this is the text to embed".
    embedding: the vector representation of `content`. Marked as the
        embedding model's VectorField, so LanceDB computes it automatically
        from `content` — you never set it by hand (see ingestion.py).
    """
    doc_id: str
    filepath: str
    filename: str
    content: str = embedding_model.SourceField()
    embedding: Vector(embedding_model.ndims()) = embedding_model.VectorField()


class Prompt(BaseModel):
    """
    The request body api.py's /rag/query endpoint expects — just the
    user's question as plain text.
    """
    prompt: str


class RagResponse(BaseModel):
    """
    The shape rag_agent (in rag.py) is forced to answer in, via
    `output_type=RagResponse`. pydantic-ai makes the LLM fill in exactly
    these fields instead of returning free-form text.

    answer: the actual answer to the user's question.
    source: which file(s) the answer was based on, since rag_agent's
        instructions tell it to always cite its source.
    """
    answer: str
    source: str
