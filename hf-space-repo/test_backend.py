import requests
import json

print("Testing backend...")
try:
    payload = {
        "query": "what is ros",
        "messages": [],
        "top_k": 3
    }
    response = requests.post("http://localhost:8000/chat", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
