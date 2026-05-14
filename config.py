import os
from dotenv import load_dotenv

load_dotenv()

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

_gcp_project    = os.getenv("GOOGLE_CLOUD_PROJECT", "yansheng-project")
_gcp_region     = os.getenv("GOOGLE_CLOUD_REGION", "us-central1")
GEMINI_BASE_URL = f"https://{_gcp_region}-aiplatform.googleapis.com/v1beta1/projects/{_gcp_project}/locations/{_gcp_region}/endpoints/openapi/"

GEMINI_FLASH = "google/gemini-2.5-flash"
GEMINI_PRO   = "google/gemini-2.5-pro"
LLM_MODEL    = GEMINI_FLASH  # default model

EMBEDDING_MODEL = "BAAI/bge-m3"
COLLECTION_NAME = "ai_docs"
VECTOR_SIZE = 1024  # bge-m3の出力次元数