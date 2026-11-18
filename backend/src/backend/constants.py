"""
Shared file-path constants for the whole backend, so every script points at
the same folders instead of each hardcoding its own copy of the path.

Used by:
- pdfs_to_text.py: reads PDFs from DATA_PATH, writes .txt files back into it.
- ingestion.py: reads the .txt files from DATA_PATH, writes the vector
  database into VECTOR_DATABASE_PATH.
- rag.py (planned, not yet written): will read the vector database back
  out of VECTOR_DATABASE_PATH to answer questions.
"""

from pathlib import Path

# Folder holding raw source documents: the original PDFs plus the .txt
# files extracted from them by pdfs_to_text.py.
# __file__ is this file, i.e. backend/src/backend/constants.py.
# .parents[0] is backend/src/backend/, .parents[1] is backend/src/ —
# so this points at backend/src/data/.
DATA_PATH = Path(__file__).parents[1]/"data"

# Folder where the LanceDB vector database lives on disk (backend/src/knowledge_base/).
# A single source of truth: ingestion.py writes here, rag.py will read from here.
VECTOR_DATABASE_PATH = Path(__file__).parents[1] / "knowledge_base"