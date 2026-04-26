import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

EMBEDDING_MODEL = "BAAI/bge-m3"
LLM_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
COLLECTION_NAME = "ai_docs"
VECTOR_SIZE = 1024  # bge-m3 输出维度