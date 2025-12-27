"""Configuration settings for RAG backend."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent
DOCS_PATH = Path(os.getenv("DOCS_PATH", "../docs")).resolve()

# Gemini API (for embeddings and completions)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Qdrant Configuration
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", None)
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "humanoid_robotics_book")

# Embedding Model (Gemini)
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/text-embedding-004")
EMBEDDING_DIMENSION = 768  # Gemini text-embedding-004 outputs 768 dimensions

# Chunking Settings
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# Retrieval Settings
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" or "groq"
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-1.5-flash")
MAX_CONTEXT_TOKENS = 4000

# Groq API (alternative LLM provider)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Database Configuration (Neon)
DATABASE_URL = os.getenv("DATABASE_URL", None)
