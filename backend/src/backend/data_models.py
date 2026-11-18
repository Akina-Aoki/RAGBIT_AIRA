"""
This is the shared vocabulary of the whole project. 
Article describes what gets stored; 
Prompt describes what comes in from the user; 
RagResponse describes what goes out as the answer.
"""

import os
from pydantic import BaseModel, Field
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector
from dotenv import load_dotenv

# Loads variables from a .env file (e.g. the Gemini API key) into the environment
# so the embedding model below can authenticate.
load_dotenv()

embedding_model = get_registry().get("cohere").create(name="embed-multilingual-v3.0")

class Article(LanceModel):
    doc_id: str
    filepath: str
    filename: str
    content: str = embedding_model.SourceField()
    embedding: Vector(embedding_model.ndims()) = embedding_model.VectorField()
