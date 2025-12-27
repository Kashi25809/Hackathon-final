# Physical AI & Humanoid Robotics Textbook

A comprehensive, open-source digital textbook on Physical AI and Humanoid Robotics, featuring a RAG-powered chatbot assistant.

## 🚀 Project Overview

This repository contains:
- **Docusaurus Frontend**: A documentation-based website for the textbook.
- **RAG Backend**: A FastAPI-based Python backend that provides intelligent answers based on the textbook content.
- **AI Integration**: Uses Gemini for embeddings and Groq (Llama 3.3) for fast, context-aware responses.
- **Vector Search**: Powered by Qdrant.
- **Analytics**: Chat interactions logged to a Neon PostgreSQL database.

## 📁 Repository Structure

- `/my-website`: The Docusaurus frontend and core content.
- `/my-website/rag-backend`: The Python RAG API.
- `/docs`: The source markdown files for the textbook (located within `my-website`).

## 🛠 Tech Stack

- **Frontend**: React, Docusaurus, CSS.
- **Backend**: Python, FastAPI, SQLAlchemy.
- **AI/ML**: Google Gemini (Embeddings), Groq/Llama 3.3 (LLM).
- **Database**: Qdrant (Vector), Neon PostgreSQL (Relational).
- **Deployment**: Vercel (Frontend), Hugging Face Spaces (Backend).

## 🚀 Getting Started

### Backend Setup
1. Navigate to `my-website/rag-backend`.
2. Install dependencies: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env` and fill in your API keys.
4. Run the server: `python main.py`.

### Frontend Setup
1. Navigate to `my-website`.
2. Install dependencies: `npm install`.
3. Start the dev server: `npm start`.

## 📄 License

MIT
