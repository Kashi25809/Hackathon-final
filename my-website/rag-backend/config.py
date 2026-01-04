"""Configuration settings for RAG backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DOCS_PATH = Path(os.getenv("DOCS_PATH", "docs")).resolve()

# Groq API
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Embedding Model (Sentence Transformers)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 outputs 384 dimensions

# Chunking Settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Retrieval Settings
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "groq")
LLM_MODEL = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
MAX_CONTEXT_TOKENS = 4000

# Database Configuration (Neon)
DATABASE_URL = os.getenv("DATABASE_URL", None)
