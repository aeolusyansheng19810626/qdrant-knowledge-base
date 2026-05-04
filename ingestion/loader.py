from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    SparseVectorParams, SparseIndexParams,
    PayloadSchemaType, SparseVector,
)
from sentence_transformers import SentenceTransformer
from fastembed import SparseTextEmbedding
from pypdf import PdfReader
import re
import uuid
import streamlit as st
from config import QDRANT_URL, QDRANT_API_KEY, EMBEDDING_MODEL, COLLECTION_NAME, VECTOR_SIZE

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)

@st.cache_resource
def get_dense_embedder():
    return SentenceTransformer(EMBEDDING_MODEL)

@st.cache_resource
def get_sparse_embedder():
    return SparseTextEmbedding(model_name="Qdrant/bm25")

def ensure_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={
                "dense": VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams(on_disk=False)
                )
            },
        )
    
    # インデックスの存在を確認（既存の場合はスキップまたは上書き）
    for field in ["framework", "doc_type", "filename"]:
        client.create_payload_index(
            collection_name=COLLECTION_NAME,
            field_name=field,
            field_schema=PayloadSchemaType.KEYWORD,
        )

def extract_text(file) -> str:
    filename = file.name.lower()
    if filename.endswith(".pdf"):
        reader = PdfReader(file)
        return "\n".join(page.extract_text() for page in reader.pages if page.extract_text())
    elif filename.endswith(".md"):
        content = file.read()
        if isinstance(content, bytes):
            content = content.decode("utf-8")
        # Markdown構文記号を除去し、プレーンテキストのみ保持
        content = re.sub(r'#{1,6}\s+', '', content)       # 見出し
        content = re.sub(r'\*{1,2}(.+?)\*{1,2}', r'\1', content)  # 太字/斜体
        content = re.sub(r'`{1,3}[^`]*`{1,3}', '', content)       # コードブロック
        content = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', content)      # リンク
        content = re.sub(r'^\s*[-*+]\s+', '', content, flags=re.MULTILINE)  # リスト
        return content
    else:
        raise ValueError(f"不支持的文件类型：{filename}")

def split_into_sentences(text: str) -> list[str]:
    """文を境界で分割"""
    text = re.sub(r'\s+', ' ', text).strip()
    sentences = re.split(r'(?<=[.!?。！？])\s+', text)
    sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
    return sentences

def chunk_by_sentences(sentences: list[str], chunk_size: int = 8, overlap: int = 2) -> list[str]:
    """文の数でチャンク分割（オーバーラップあり）"""
    chunks = []
    i = 0
    while i < len(sentences):
        chunk = " ".join(sentences[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks

def upload_document(file, framework: str, doc_type: str) -> int:
    ensure_collection()
    dense_embedder = get_dense_embedder()
    sparse_embedder = get_sparse_embedder()

    text = extract_text(file)
    sentences = split_into_sentences(text)
    chunks = chunk_by_sentences(sentences)

    dense_vectors = dense_embedder.encode(chunks, show_progress_bar=False).tolist()
    sparse_results = list(sparse_embedder.embed(chunks))

    points = []
    for i, (chunk, dense_vec, sparse_vec) in enumerate(zip(chunks, dense_vectors, sparse_results)):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector={
                "dense": dense_vec,
                "sparse": SparseVector(
                    indices=sparse_vec.indices.tolist(),
                    values=sparse_vec.values.tolist(),
                ),
            },
            payload={
                "text": chunk,
                "framework": framework,
                "doc_type": doc_type,
                "filename": file.name,
                "chunk_index": i,
            }
        ))

    batch_size = 10
    for i in range(0, len(points), batch_size):
        batch = points[i:i + batch_size]
        client.upsert(collection_name=COLLECTION_NAME, points=batch)
    return len(points)