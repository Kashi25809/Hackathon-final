---
sidebar_label: "API Reference"
sidebar_position: 3
---

# API Reference

Complete documentation for the RAG Chatbot FastAPI endpoints.

**Base URL:** `http://localhost:8000`

---

## Chat Endpoints

### POST /chat

Query the chatbot with a question.

**Request Body:**
```json
{
  "query": "What is ROS 2?",
  "top_k": 5,
  "include_sources": true
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | - | User's question |
| `top_k` | integer | No | 5 | Number of passages to retrieve |
| `include_sources` | boolean | No | true | Include source citations |

**Response:**
```json
{
  "answer": "ROS 2 (Robot Operating System 2) is a flexible framework for writing robot software. It provides tools and libraries for building robot applications, including communication primitives like nodes, topics, services, and actions...",
  "sources": [
    {
      "title": "ROS 2 Architecture",
      "file_path": "01-robotic-nervous-system/ros2-architecture.md",
      "module": "01-robotic-nervous-system",
      "score": 0.847
    }
  ],
  "query": "What is ROS 2?",
  "model": "gpt-4o-mini"
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "How does domain randomization work in Isaac Sim?"}'
```

---

### POST /search

Search for relevant passages without generating a response.

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query |
| `top_k` | integer | No | 5 | Number of results |
| `module` | string | No | - | Filter by module |

**Response:**
```json
{
  "query": "domain randomization",
  "results": [
    {
      "content": "Domain randomization varies simulation parameters...",
      "score": 0.823,
      "metadata": {
        "file_path": "03-ai-robot-brain/isaac-sim.md",
        "title": "Isaac Sim",
        "module": "03-ai-robot-brain"
      }
    }
  ],
  "count": 5
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/search?query=SLAM&top_k=3"
```

---

## Admin Endpoints

### POST /ingest

Ingest or re-ingest all documents from the docs folder.

:::warning
This will recreate the Qdrant collection and reprocess all documents.
:::

**Response:**
```json
{
  "status": "success",
  "message": "Successfully ingested 20 documents",
  "documents_processed": 20,
  "chunks_created": 142
}
```

**Example:**
```bash
curl -X POST http://localhost:8000/ingest
```

---

### GET /stats

Get vector collection statistics.

**Response:**
```json
{
  "collection_name": "humanoid_robotics_book",
  "vectors_count": 142,
  "points_count": 142,
  "status": "green"
}
```

---

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "qdrant_connected": true,
  "openai_configured": true
}
```

---

## Error Responses

| Status Code | Description |
|-------------|-------------|
| 400 | Bad request (empty query) |
| 500 | Internal server error |
| 503 | Service unavailable (Qdrant down) |

**Error Format:**
```json
{
  "detail": "Error message here"
}
```

---

## Interactive Docs

FastAPI provides automatic interactive documentation:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

:::info Next Steps
See the [Integration Guide](./integration) to connect the API with the frontend.
:::
