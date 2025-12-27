"""Test Gemini API connection."""
import os
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
print(f"Gemini API Key present: {bool(gemini_key)}")
print(f"Gemini API Key: {gemini_key[:10]}...{gemini_key[-5:]}" if gemini_key else "Not set")
print()

try:
    from google import genai
    
    print("Creating Gemini client...")
    client = genai.Client(api_key=gemini_key)
    
    print("Testing embedding...")
    result = client.models.embed_content(
        model="models/text-embedding-004",
        contents="Hello world"
    )
    print(f"Embedding successful! Dimension: {len(result.embeddings[0].values)}")
    
    print("\nTesting generation...")
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents="Say hello in one word"
    )
    print(f"Generation successful! Response: {response.text}")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
