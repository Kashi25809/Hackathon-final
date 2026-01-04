# RAG Chatbot Module - Complete Documentation

## 📋 Overview

This module contains the complete documentation and implementation for the **Retrieval-Augmented Generation (RAG) Chatbot** - an AI assistant that answers questions about the Physical AI & Humanoid Robotics textbook.

## ✅ Completion Status

### Documentation (100% Complete)
- ✅ **index.md** - Main overview with architecture and quick start
- ✅ **setup.md** - Complete installation and configuration guide
- ✅ **api-reference.md** - Full API endpoint documentation
- ✅ **integration.md** - Frontend integration guide

### Backend Implementation (100% Complete)
Located in `my-website/rag-backend/`:
- ✅ **config.py** - Configuration management
- ✅ **ingest.py** - Document ingestion pipeline
- ✅ **retrieval.py** - Semantic search functionality
- ✅ **generation.py** - Response generation with Groq
- ✅ **main.py** - FastAPI application
- ✅ **database.py** - Qdrant vector database integration
- ✅ **models.py** - Pydantic data models
- ✅ **tests/test_pipeline.py** - Unit tests

### Frontend Integration (100% Complete)
Located in `my-website/src/`:
- ✅ **components/ChatWidget/ChatWidget.tsx** - React chat component
- ✅ **components/ChatWidget/ChatWidget.css** - Widget styling
- ✅ **theme/Root.tsx** - Global integration

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│  (Docusaurus + React ChatWidget)                           │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP REST API
┌────────────────────▼────────────────────────────────────────┐
│                  FastAPI Backend                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Retrieval  │  │  Generation  │  │   Ingestion  │     │
│  │   (Search)   │  │  (Groq LLM)  │  │  (Pipeline)  │     │
│  └──────┬───────┘  └──────────────┘  └──────┬───────┘     │
└─────────┼──────────────────────────────────┼──────────────┘
          │                                    │
┌─────────▼────────────────────────────────────▼──────────────┐
│              Qdrant Vector Database                         │
│  (Stores embeddings of all textbook content)               │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Embeddings** | `all-MiniLM-L6-v2` | Convert text to 384-dim vectors |
| **Vector Store** | Qdrant | Semantic search & storage |
| **LLM** | Groq (Llama 3.3 70B) | Generate grounded responses |
| **Backend** | FastAPI + Python 3.10+ | REST API server |
| **Frontend** | React + TypeScript | Chat widget UI |

## 🚀 Quick Start

### 1. Start Backend
```bash
cd my-website/rag-backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your GROQ_API_KEY

# Start Qdrant
docker run -d -p 6333:6333 qdrant/qdrant

# Ingest documents
python ingest.py

# Start API server
uvicorn main:app --reload
```

### 2. Start Frontend
```bash
cd my-website

# Install dependencies (if not already done)
npm install

# Start Docusaurus
npm start
```

### 3. Test
- Open http://localhost:3000
- Look for the chat button in the bottom-right corner
- Ask: "What is ROS 2?"

## 📚 Documentation Structure

```
05-rag-chatbot/
├── index.md           # Main overview & architecture
├── setup.md           # Installation guide
├── api-reference.md   # API endpoints
├── integration.md     # Frontend integration
└── README.md          # This file
```

## 🔗 Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/chat` | POST | Ask questions and get grounded answers |
| `/search` | POST | Search for relevant passages |
| `/health` | GET | Check system health |
| `/stats` | GET | Get collection statistics |
| `/ingest` | POST | Re-ingest all documents |

## 🎯 Features

- ✅ **Semantic Search** - Find relevant content using vector similarity
- ✅ **Grounded Responses** - Answers backed by source citations
- ✅ **Real-time Chat** - Interactive chat widget on every page
- ✅ **Dark Mode Support** - Automatically adapts to theme
- ✅ **Source Citations** - Shows which documents were used
- ✅ **Module Filtering** - Search within specific modules
- ✅ **CORS Enabled** - Ready for cross-origin requests

## 🧪 Testing

```bash
# Run all tests
cd my-website/rag-backend
pytest tests/test_pipeline.py -v

# Test specific components
pytest tests/test_pipeline.py::TestEmbeddingGenerator -v
```

## 🔐 Environment Variables

Required in `rag-backend/.env`:
```bash
GROQ_API_KEY=gsk_your_key_here
QDRANT_URL=http://localhost:6333
QDRANT_COLLECTION_NAME=humanoid_robotics_book
EMBEDDING_MODEL=all-MiniLM-L6-v2
DOCS_PATH=../docs
```

## 📊 Performance

- **Embedding Model**: 384 dimensions (all-MiniLM-L6-v2)
- **Average Query Time**: ~500ms
- **Chunk Size**: 500 characters
- **Chunk Overlap**: 100 characters
- **Default Top-K**: 5 passages

## 🐛 Common Issues

### Backend won't start
- Check if Qdrant is running: `docker ps | grep qdrant`
- Verify GROQ_API_KEY is set in `.env`

### No results from search
- Run ingestion: `python ingest.py`
- Check Qdrant has data: `curl http://localhost:6333/collections/humanoid_robotics_book`

### Chat widget not appearing
- Verify Root.tsx imports ChatWidget
- Check browser console for errors
- Ensure backend is running on port 8000

## 🚀 Deployment

### Backend (Hugging Face Spaces)
1. Create a new Space (Gradio/Docker)
2. Add secrets: `GROQ_API_KEY`, `QDRANT_URL`, `QDRANT_API_KEY`
3. Push backend code
4. Update frontend `apiUrl` to Space URL

### Frontend (Vercel)
1. Deploy Docusaurus site to Vercel
2. Set environment variable: `RAG_API_URL=https://your-space.hf.space`
3. Update CORS in backend to allow Vercel domain

## 📖 Related Modules

- **Module 01**: Robotic Nervous System (ROS 2)
- **Module 02**: Digital Twin (Gazebo & Unity)
- **Module 03**: AI-Robot Brain (NVIDIA Isaac)
- **Module 04**: Vision-Language-Action

The RAG chatbot can answer questions about all these modules!

## 🤝 Contributing

To add new content to the chatbot:
1. Add markdown files to `docs/` directory
2. Run `python ingest.py` to re-index
3. Test with relevant queries

## 📝 Notes

- The chatbot uses **Groq** (not OpenAI) for fast inference
- Embeddings are generated **locally** (no API calls)
- Qdrant can run locally (Docker) or in the cloud
- All documentation is in Markdown format
- The widget is globally available on all pages

---

**Status**: ✅ Complete and Production Ready

**Last Updated**: January 4, 2026
