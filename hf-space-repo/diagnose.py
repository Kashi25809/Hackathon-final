
import os
from dotenv import load_dotenv
import requests

load_dotenv()

print("--- Diagnostics ---")
gemini_key = os.getenv("GEMINI_API_KEY")
print(f"Gemini API Key present: {bool(gemini_key)}")
if gemini_key:
    # Check if it looks valid (basic check)
    print(f"Gemini API Key length: {len(gemini_key)}")

qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
print(f"Qdrant URL: {qdrant_url}")

try:
    response = requests.get(qdrant_url)
    print(f"Qdrant Connection: {response.status_code}")
    print(f"Qdrant Response: {response.text}")
except Exception as e:
    print(f"Qdrant Connection Failed: {e}")
