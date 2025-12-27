"""Test Qdrant connection directly."""
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
collection_name = os.getenv("QDRANT_COLLECTION_NAME", "humanoid_robotics_book")

print(f"Qdrant URL: {qdrant_url}")
print(f"API Key present: {bool(qdrant_api_key)}")
print(f"API Key length: {len(qdrant_api_key) if qdrant_api_key else 0}")
print(f"Collection: {collection_name}")
print()

try:
    print("Connecting to Qdrant...")
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    
    print("Getting collections...")
    collections = client.get_collections()
    print(f"Collections: {collections}")
    
    print(f"\nChecking collection '{collection_name}'...")
    try:
        info = client.get_collection(collection_name)
        print(f"Collection exists!")
        print(f"  Vectors count: {info.vectors_count}")
        print(f"  Points count: {info.points_count}")
        print(f"  Status: {info.status}")
    except Exception as e:
        print(f"Collection not found or error: {e}")
        
except Exception as e:
    print(f"Connection Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
