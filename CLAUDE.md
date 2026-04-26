# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

RAG-based AI Technical Documentation Q&A System. Users upload PDF/Markdown docs, then query them via a Streamlit chat UI. Retrieval combines semantic and keyword search with LLM-powered answers. Each Q&A is automatically evaluated by RAGAS and scores are shown inline.

## Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run app.py
```

The app runs at http://localhost:8501. On first run, two ML models download (~1.1 GB total):
- `BAAI/bge-m3` (~570 MB) — dense embeddings
- `BAAI/bge-reranker-v2-m3` (~570 MB) — reranker

No test suite exists; testing is done via the Streamlit UI.

## Environment Variables

Requires a `.env` file in the project root:
```
GROQ_API_KEY=...
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=...
```

All credentials and model names are centralized in [config.py](config.py).

## Architecture

```
app.py  →  ingestion/loader.py   →  Qdrant Cloud ("ai_docs" collection)
app.py  →  retrieval/search.py   →  Qdrant + Groq LLM
app.py  →  evaluation/evaluator.py  →  RAGAS + Groq LLM
```

**Ingestion pipeline** ([ingestion/loader.py](ingestion/loader.py)):
1. Extract text from PDF (pypdf) or Markdown (regex cleanup)
2. Split into sentences (≥20 chars), chunk into groups of 8 with 2-sentence overlap
3. Embed with `bge-m3` (dense, 1024-dim) and BM25 via fastembed (sparse)
4. Store in Qdrant with payload: `{text, framework, doc_type, filename, chunk_index}`

**Retrieval pipeline** ([retrieval/search.py](retrieval/search.py)):
1. Encode query as dense + sparse vectors
2. Hybrid search: Dense Prefetch(20) + Sparse Prefetch(20) fused with RRF
3. Rerank Top-20 with `bge-reranker-v2-m3` CrossEncoder → select Top-5
4. Assemble context and generate answer via Groq API (Llama 4 Scout)

**Evaluation pipeline** ([evaluation/evaluator.py](evaluation/evaluator.py)):
- Runs after each answer via `run_evaluation(query, answer, contexts)`
- Uses `LangchainLLMWrapper(ChatGroq(...))` as the RAGAS LLM (same Groq key as the main LLM)
- Reuses the already-cached `bge-m3` instance via `_STEmbeddings` — no second model load
- Metrics: `Faithfulness`, `AnswerRelevancy`, `LLMContextPrecisionWithoutReference` (last one requires ragas ≥ 0.2.6)
- Returns `None` silently on any failure; scores displayed with `st.status` in the UI

**Key design choices:**
- All ML models are cached with `@st.cache_resource` to avoid reloading per request
- `ensure_collection()` is idempotent — safe to call on every app start
- Payload indices on `framework`, `doc_type`, `filename` enable efficient filtering
- Deleting a document by filename removes all chunks from the collection in one scroll+delete pass
- `sources` dict from `search()` carries both `text` (200-char truncated, for UI) and `text_full` (for RAGAS)

## Known Temporary Code

Two `print()` debug statements exist at [retrieval/search.py:89-90](retrieval/search.py#L89) (pre/post rerank point IDs). These should be removed before production deployment.

## Tunable Parameters

| Parameter | Location | Default |
|-----------|----------|---------|
| Chunk size | `loader.py` `chunk_by_sentences()` | 8 sentences |
| Chunk overlap | `loader.py` `chunk_by_sentences()` | 2 sentences |
| Dense/sparse prefetch limit | `search.py` Prefetch calls | 20 each |
| Final top_k | `search.py` `search()` | 5 |
| Embedding model | `config.py` `EMBEDDING_MODEL` | `BAAI/bge-m3` |
| LLM model | `config.py` `LLM_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` |
| Qdrant collection | `config.py` `COLLECTION_NAME` | `ai_docs` |
