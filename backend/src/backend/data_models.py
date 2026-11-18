"""
This is the shared vocabulary of the whole project — the data shapes that
ingestion.py and rag.py pass around, defined once here so both sides agree.

Article describes what gets stored in the vector database (one row per
source document, built by ingestion.py).

Prompt (what comes in from the user) and RagResponse (what goes out as the
answer) are planned for rag.py but not written yet.
"""

import os
from pydantic import BaseModel, Field
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from pydantic import BaseModel, Field
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
    This is the shape of what a user sends in when they ask a question.
    FastAPI (in api.py) uses this to check that an incoming request
    actually contains a "prompt" field with text in it, and rejects
    anything that doesn't match.
    """
    prompt: str = Field(description = "prompt from user, if empty consider prompt as missing.")


class RagResponse(BaseModel):
    """
    This is the shape we FORCE the AI's answer into. Instead of letting
    the AI just reply with free-form text, we tell it: your answer must
    fill in exactly these three fields. That makes the response
    predictable and easy for app.py (the Streamlit page) to read.
    """
    filename: str = Field(description="filename of the retrieved file without suffix")
    filepath: str = Field(description="absolute path to the retrieved file")
    answer: str = Field(description="answer based on the retrieved file")