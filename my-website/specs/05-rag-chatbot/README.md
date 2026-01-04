# Module 05: RAG Chatbot Integration

**Status:** ✅ Complete  
**Focus:** Intelligent Assistance & Production

## 🎯 Learning Objectives

- Understand Retrieval-Augmented Generation (RAG) architecture.
- Implement vector search using Qdrant.
- Integrate LLMs (Groq) for knowledge-grounded answers.
- Deploy a production-ready chatbot to the web.

## 📚 Content Structure

The module content is located in `docs/05-rag-chatbot/`:

| File | Topic | Description |
|------|-------|-------------|
| `index.md` | Overview | RAG concepts and goals |
| `setup.md` | Configuration | Environment and dependencies |
| `api-reference.md` | Interface | FastAPI endpoints |
| `integration.md` | Frontend | React ChatWidget implementation |

## 🛠️ Technical Implementation

### System Stack
- **Languages**: Python (Backend), TypeScript (Frontend)
- **Frameworks**: FastAPI, React
- **Database**: Qdrant (Vectors), Neon PostgreSQL (Logs)
- **AI Models**: 
  - Embeddings: `sentence-transformers/all-MiniLM-L6-v2`
  - Generation: `Groq/llama-3.3-70b-versatile`

### Components
1. **Ingestion Pipeline**: Chunking and embedding markdown docs.
2. **Vector Store**: Storing embeddings for semantic search.
3. **Chat API**: `POST /chat` endpoint for handling user queries.
4. **UI Widget**: Floating chat component in Docusaurus.

## ✅ Deliverables

1. **RAG Backend**: A FastAPI service deployed on Hugging Face Spaces.
2. **Chat Interface**: A responsive widget integrated into the textbook website.
3. **Deployed System**: User-facing chatbot capable of answering questions about the course material.
