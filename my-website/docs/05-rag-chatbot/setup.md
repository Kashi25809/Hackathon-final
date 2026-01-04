---
sidebar_label: "Setup Guide"
sidebar_position: 2
---

# Setup Guide

Complete installation and configuration guide for the RAG chatbot backend.

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.10+ | Runtime |
| Docker | Latest | Qdrant database |
| Groq API Key | - | Chat completions |

---

## Step 1: Install Dependencies

```bash
cd my-website/rag-backend
pip install -r requirements.txt
```

Key packages installed:
- `fastapi` + `uvicorn` — Web server
- `sentence-transformers` — Local embeddings
- `qdrant-client` — Vector database
- `groq` — Chat completions

---

## Step 2: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```bash title=".env"
# Required: Groq API key for chat completions
GROQ_API_KEY=gsk_your_key_here

# Qdrant (local Docker)
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=

# Or Qdrant Cloud
# QDRANT_URL=https://your-cluster.qdrant.io
# QDRANT_API_KEY=your-api-key
```

---

## Step 3: Start Qdrant

### Option A: Docker (Recommended)

```bash
docker run -d -p 6333:6333 -p 6334:6334 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

### Option B: Qdrant Cloud

1. Create account at [cloud.qdrant.io](https://cloud.qdrant.io)
2. Create a cluster
3. Copy URL and API key to `.env`

---

## Step 4: Ingest Documents

Run the ingestion pipeline to process book content:

```bash
python ingest.py
```

Expected output:
```
==================================================
RAG Ingestion Pipeline
==================================================

[1/4] Loading documents...
Loaded 20 markdown files

[2/4] Chunking documents...
  - ros2-architecture: 12 chunks
  - isaac-sim: 15 chunks
  ...
Total chunks: 142

[3/4] Generating embeddings...
Batches: 100%|██████████| 3/3

[4/4] Storing in Qdrant...
Created collection 'humanoid_robotics_book'
Total points upserted: 142

==================================================
Ingestion Complete!
==================================================
```

---

## Step 5: Start the Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify at: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## Step 6: Test the API

```bash
# Health check
curl http://localhost:8000/health

# Chat query
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "What are ROS 2 nodes?"}'
```

---

## Configuration Reference

| Variable | Default | Description |
|----------|---------|-------------|
| `GROQ_API_KEY` | - | Required for chat |
| `QDRANT_URL` | `http://localhost:6333` | Vector database URL |
| `QDRANT_COLLECTION_NAME` | `humanoid_robotics_book` | Collection name |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Sentence transformer model |
| `CHUNK_SIZE` | `500` | Characters per chunk |
| `CHUNK_OVERLAP` | `100` | Overlap between chunks |
| `DOCS_PATH` | `../docs` | Path to markdown files |

---

## Troubleshooting

### "Connection refused" to Qdrant
```bash
# Check if Qdrant is running
docker ps | grep qdrant

# Restart if needed
docker restart <container_id>
```

### "No documents found"
- Verify `DOCS_PATH` points to the docs directory
- Check for `.md` files in the path

### Groq API errors
- Verify API key is valid (starts with `gsk_`)
- Check rate limits in Groq console

:::info Next Steps
Once the backend is running, proceed to the [API Reference](./api-reference) to understand the available endpoints.
:::
