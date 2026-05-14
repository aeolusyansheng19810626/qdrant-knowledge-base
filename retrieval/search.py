from qdrant_client import QdrantClient
from qdrant_client.models import (
    Filter, FieldCondition, MatchValue, MatchAny,
    FusionQuery, Prefetch, Fusion,
    SparseVector,
)
from sentence_transformers import SentenceTransformer, CrossEncoder
from fastembed import SparseTextEmbedding
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import streamlit as st
from config import (
    QDRANT_URL, QDRANT_API_KEY, EMBEDDING_MODEL,
    COLLECTION_NAME, GEMINI_API_KEY, GEMINI_BASE_URL, LLM_MODEL
)

RERANKER_MODEL = "BAAI/bge-reranker-v2-m3"

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)
llm = ChatOpenAI(api_key=GEMINI_API_KEY, base_url=GEMINI_BASE_URL, model=LLM_MODEL)

@st.cache_resource
def get_dense_embedder():
    return SentenceTransformer(EMBEDDING_MODEL)

@st.cache_resource
def get_sparse_embedder():
    return SparseTextEmbedding(model_name="Qdrant/bm25")

@st.cache_resource
def get_reranker():
    return CrossEncoder(RERANKER_MODEL)

def build_filter(framework: str = None, doc_type: str = None):
    conditions = []
    all_vals = {"全部", "All", "すべて"}
    if framework and framework not in all_vals:
        conditions.append(FieldCondition(key="framework", match=MatchValue(value=framework)))
    if doc_type and doc_type not in all_vals:
        doc_type_equivalents = {
            "教程": ["教程", "Tutorial", "ﾁｭｰﾄﾘｱﾙ", "チュートリアル"],
            "Tutorial": ["教程", "Tutorial", "ﾁｭｰﾄﾘｱﾙ", "チュートリアル"],
            "ﾁｭｰﾄﾘｱﾙ": ["教程", "Tutorial", "ﾁｭｰﾄﾘｱﾙ", "チュートリアル"],
            "チュートリアル": ["教程", "Tutorial", "ﾁｭｰﾄﾘｱﾙ", "チュートリアル"],

            "API文档": ["API文档", "API Docs", "API ﾄﾞｷｭﾒﾝﾄ", "API ドキュメント"],
            "API Docs": ["API文档", "API Docs", "API ﾄﾞｷｭﾒﾝﾄ", "API ドキュメント"],
            "API ﾄﾞｷｭﾒﾝﾄ": ["API文档", "API Docs", "API ﾄﾞｷｭﾒﾝﾄ", "API ドキュメント"],
            "API ドキュメント": ["API文档", "API Docs", "API ﾄﾞｷｭﾒﾝﾄ", "API ドキュメント"],

            "其他": ["其他", "Other", "その他"],
            "Other": ["其他", "Other", "その他"],
            "その他": ["其他", "Other", "その他"],
            
            "changelog": ["changelog"]
        }
        
        # 查找等价列表，如果存在则用 MatchAny，否则用 MatchValue
        eq_list = doc_type_equivalents.get(doc_type)
        if eq_list:
            conditions.append(FieldCondition(key="doc_type", match=MatchAny(any=eq_list)))
        else:
            conditions.append(FieldCondition(key="doc_type", match=MatchValue(value=doc_type)))
            
    return Filter(must=conditions) if conditions else None

def search(query: str, framework: str = None, doc_type: str = None, top_k: int = 5, lang: str = "zh") -> tuple[str, list[dict]]:
    dense_embedder = get_dense_embedder()
    sparse_embedder = get_sparse_embedder()
    reranker = get_reranker()

    # 1. クエリベクトルの生成
    dense_vector = dense_embedder.encode(query).tolist()
    sparse_result = list(sparse_embedder.embed([query]))[0]
    sparse_vector = SparseVector(
        indices=sparse_result.indices.tolist(),
        values=sparse_result.values.tolist(),
    )

    query_filter = build_filter(framework, doc_type)

    # 2. ハイブリッド検索でTop-20を取得
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            Prefetch(
                query=dense_vector,
                using="dense",
                filter=query_filter,
                limit=20,
            ),
            Prefetch(
                query=sparse_vector,
                using="sparse",
                filter=query_filter,
                limit=20,
            ),
        ],
        query=FusionQuery(fusion=Fusion.RRF),
        limit=20,
        with_payload=True,
    ).points

    if not results:
        no_doc_msg = {
            "zh": "未找到相关文档，请尝试调整过滤条件或关键词。",
            "en": "No relevant documents found. Please try adjusting filters or keywords.",
            "ja": "関連ドキュメントが見つかりませんでした。フィルター条件やキーワードを調整して再試行してください。"
        }
        return no_doc_msg.get(lang, "未找到相关文档，请尝试调整过滤条件或关键词。"), []

    # 3. Rerankerで再ランキング、Top-kを取得
    texts = [r.payload["text"] for r in results]
    pairs = [[query, text] for text in texts]
    scores = reranker.predict(pairs)

    reranked_with_scores = sorted(zip(scores, results), key=lambda x: x[0], reverse=True)
    
    print("rerank前:", [r.id for r in results])
    print("rerank后:", [r.id for score, r in reranked_with_scores])
    
    top_ranked = reranked_with_scores[:top_k]

    # 4. ソース情報とコンテキストの組み立て
    sources = []
    context_parts = []
    for score, r in top_ranked:
        payload = r.payload
        sources.append({
            "filename": payload.get("filename", "未知"),
            "framework": payload.get("framework", "未知"),
            "doc_type": payload.get("doc_type", "未知"),
            "chunk_index": payload.get("chunk_index", 0),
            "score": round(float(score), 4),
            "text": payload.get("text", "")[:200],
            "text_full": payload.get("text", ""),
        })
        context_parts.append(
            f"[{payload.get('framework')} / {payload.get('doc_type')}]\n{payload.get('text')}"
        )

    context = "\n\n".join(context_parts)
    
    lang_instructions = {
        "zh": "用中文回答",
        "en": "Please answer in English",
        "ja": "日本語で回答してください"
    }
    lang_instruction = lang_instructions.get(lang, "用中文回答")
    
    messages = [
        SystemMessage(content=f"你是一个 AI 技术文档助手。根据以下文档内容回答用户问题，{lang_instruction}，回答要简洁准确。"),
        HumanMessage(content=f"文档内容：\n{context}\n\n问题：{query}"),
    ]
    response = llm.invoke(messages)
    return response.content, sources