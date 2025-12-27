"""Response generation module supporting Gemini and Groq LLMs."""

from typing import List, Dict, Any, Optional
import time
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

import config
from models import ChatMessage
from retrieval import get_retriever


# System prompt for grounded responses
SYSTEM_PROMPT = """You are a polite, knowledgeable, and friendly AI study partner called "Physical AI Assistant". 
Your goal is to help users understand the "Physical AI & Humanoid Robotics" textbook content in a natural, conversational way.

GUIDELINES:
1. **Be Human & Soft**: Avoid robotic responses. Speak like a helpful tutor or colleague. Use a warm, encouraging tone.
2. **Context-Aware**: Understand the intent behind the user's question. If they are confused, explain simply. If they ask for code, provide it with clear explanations.
3. **Grounded in Knowledge**: Base your answers primarily on the provided context sections from the book. You are an expert on this specific content.
4. **Graceful Handling**: If the provided context doesn't fully answer the question, politely explain what you know based on the book and suggest related topics from the book that might help. Don't just say "I don't know".
5. **Schema Understanding**: Adapt your response structure to the query (e.g., use bullet points for lists, code blocks for technical examples, short paragraphs for concepts).

Topics you specialize in (from the book):
- ROS 2 architecture and communication
- Digital Twins, simulation (Gazebo, Isaac Sim)
- Robot vision, SLAM, and navigation
- Vision-Language-Action (VLA) models
- Humanoid robot anatomy and brains
"""


class ResponseGenerator:
    """Generate grounded responses using Gemini or Groq."""
    
    def __init__(self):
        self.retriever = get_retriever()
        self.model = config.LLM_MODEL
        self.provider = config.LLM_PROVIDER.lower()
        
        # Initialize the appropriate client
        if self.provider == "groq":
            from groq import Groq
            self.client = Groq(api_key=config.GROQ_API_KEY)
            print(f"Using Groq LLM: {self.model}")
        else:
            from google import genai
            self.client = genai.Client(api_key=config.GEMINI_API_KEY)
            print(f"Using Gemini LLM: {self.model}")
    
    @retry(
        retry=retry_if_exception_type(Exception),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def _call_llm(self, system_prompt: str, user_prompt: str) -> str:
        """Call the LLM with retry logic."""
        if self.provider == "groq":
            return self._call_groq(system_prompt, user_prompt)
        else:
            return self._call_gemini(system_prompt, user_prompt)
    
    def _call_groq(self, system_prompt: str, user_prompt: str) -> str:
        """Call Groq API."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.4,
            max_tokens=1000
        )
        return response.choices[0].message.content
    
    def _call_gemini(self, system_prompt: str, user_prompt: str) -> str:
        """Call Gemini API."""
        from google.genai import types
        response = self.client.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4,
                max_output_tokens=1000
            )
        )
        return response.text

    def generate_response(
        self,
        query: str,
        messages: List[ChatMessage] = [],
        top_k: int = None,
        include_sources: bool = True
    ) -> Dict[str, Any]:
        """
        Generate a response grounded in book content.
        
        Args:
            query: User's question
            messages: Conversation history
            top_k: Number of passages to retrieve
            include_sources: Whether to include source citations
            
        Returns:
            Response with answer and sources
        """
        # 1. Retrieve relevant passages based on current query
        passages = self.retriever.search(query, top_k=top_k or config.TOP_K_RESULTS)
        
        # 2. Build context from passages
        context_text = self._build_context(passages)
        
        # 3. Format history
        history_text = self._format_history(messages)
        
        # 4. Construct prompt
        full_prompt = f"""Based on the following context from the Physical AI & Humanoid Robotics textbook, answer the question.

CONTEXT FROM BOOK:
{context_text}

CHAT HISTORY:
{history_text}

USER QUESTION: {query}

Provide a clear, accurate, and friendly answer based primarily on the CONTEXT provided above. If the context is empty or irrelevant, politely say so 
but try to be helpful based on your general knowledge if it's a general robotics question, while clarifying it's not in the book notes."""

        # 5. Generate response with retry
        try:
            answer = self._call_llm(SYSTEM_PROMPT, full_prompt)
        except Exception as e:
            error_str = str(e)
            if "429" in error_str or "rate" in error_str.lower():
                answer = "I'm currently receiving too many questions (Rate Limit). Please wait a moment and try again. 🤖💤"
            else:
                answer = f"I encountered an error while thinking: {error_str}"

        # 6. Format sources
        sources = []
        if include_sources and passages:
            seen_files = set()
            for p in passages:
                file_path = p["metadata"]["file_path"]
                if file_path not in seen_files:
                    sources.append({
                        "title": p["metadata"]["title"],
                        "file_path": file_path,
                        "module": p["metadata"]["module"],
                        "score": round(p["score"], 3)
                    })
                    seen_files.add(file_path)
        
        return {
            "answer": answer,
            "sources": sources,
            "query": query,
            "model": f"{self.provider}:{self.model}"
        }
    
    def _build_context(self, passages: List[Dict[str, Any]]) -> str:
        """Build context string from passages."""
        if not passages:
            return "No specific context found in the book for this query."
            
        context_parts = []
        for i, p in enumerate(passages, 1):
            title = p["metadata"]["title"]
            content = p["content"]
            context_parts.append(f"[Source {i}: {title}]\n{content}")
        
        return "\n\n---\n\n".join(context_parts)

    def _format_history(self, messages: List[ChatMessage]) -> str:
        """Format chat history for prompt."""
        if not messages:
            return "No previous history."
            
        formatted = []
        # Include recent history (last 5 messages)
        for msg in messages[-5:]: 
            role = "User" if msg.role == "user" else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        return "\n".join(formatted)


# Singleton instance
_generator_instance = None


def get_generator() -> ResponseGenerator:
    """Get or create generator singleton."""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = ResponseGenerator()
    return _generator_instance
