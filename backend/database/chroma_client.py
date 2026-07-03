import chromadb
from chromadb.config import Settings
import os

class ChromaClient:
    _instance = None
    _client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChromaClient, cls).__new__(cls)
            # persistent storage inside backend/data directory
            persist_dir = os.path.join(os.path.dirname(__file__), "..", "data", "chroma")
            os.makedirs(persist_dir, exist_ok=True)
            cls._client = chromadb.PersistentClient(path=persist_dir)
        return cls._instance

    @property
    def client(self):
        return self._client
