# RAG Backend

Retrieval-Augmented Generation chatbot backend for Physical AI & Humanoid Robotics textbook.

## Quick Start

1. **Install dependencies**:
   ```bash
   cd rag-backend
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Start Qdrant** (local option):
   ```bash
   docker run -p 6333:6333 qdrant/qdrant
   ```

4. **Ingest documents**:
   ```bash
   python ingest.py
   ```

5. **Start server**:
   ```bash
   uvicorn main:app --reload
   ```

6. **Test the API**:
   ```bash
   curl -X POST http://localhost:8000/chat \
     -H "Content-Type: application/json" \
     -d '{"query": "What is ROS 2?"}'
   ```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Query the chatbot |
| `/ingest` | POST | Ingest documents |
| `/search` | POST | Search without generation |
| `/health` | GET | Health check |
| `/stats` | GET | Collection statistics |

## Architecture

```
User Query → Embedding → Qdrant Search → Context → OpenAI → Response
```

- **Embeddings**: `all-MiniLM-L6-v2` (local, 384 dims)
- **Vector Store**: Qdrant
- **LLM**: OpenAI GPT-4o-mini
