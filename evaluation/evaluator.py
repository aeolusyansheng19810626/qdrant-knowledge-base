import math
import streamlit as st
from ragas import evaluate, EvaluationDataset, SingleTurnSample
from ragas.metrics import Faithfulness, AnswerRelevancy
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_core.embeddings import Embeddings
from langchain_groq import ChatGroq
from config import GROQ_API_KEY, LLM_MODEL
from retrieval.search import get_dense_embedder

try:
    from ragas.metrics import LLMContextPrecisionWithoutReference
    _HAS_CTX_PRECISION = True
except ImportError:
    _HAS_CTX_PRECISION = False


class _STEmbeddings(Embeddings):
    """キャッシュ済みのSentenceTransformerをラップしてbge-m3の二重ロードを回避"""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return get_dense_embedder().encode(texts).tolist()

    def embed_query(self, text: str) -> list[float]:
        return get_dense_embedder().encode(text).tolist()


@st.cache_resource
def _get_ragas_llm() -> LangchainLLMWrapper:
    return LangchainLLMWrapper(ChatGroq(api_key=GROQ_API_KEY, model=LLM_MODEL))


@st.cache_resource
def _get_ragas_embeddings() -> LangchainEmbeddingsWrapper:
    return LangchainEmbeddingsWrapper(_STEmbeddings())


def run_evaluation(query: str, answer: str, contexts: list[str]) -> dict | None:
    """RAGAS評価を実行し、{metric_key: float}の辞書を返す。失敗時はNoneを返す"""
    if not contexts:
        return None
    try:
        ragas_llm = _get_ragas_llm()
        ragas_embeddings = _get_ragas_embeddings()

        metrics = [
            Faithfulness(llm=ragas_llm),
            AnswerRelevancy(llm=ragas_llm, embeddings=ragas_embeddings),
        ]
        if _HAS_CTX_PRECISION:
            metrics.append(LLMContextPrecisionWithoutReference(llm=ragas_llm))

        sample = SingleTurnSample(
            user_input=query,
            response=answer,
            retrieved_contexts=contexts,
        )
        result = evaluate(
            dataset=EvaluationDataset(samples=[sample]),
            metrics=metrics,
            show_progress=False,
        )
        raw = result.scores[0]

        out = {}
        for display_key, raw_key in [
            ("faithfulness", "faithfulness"),
            ("answer_relevancy", "answer_relevancy"),
            ("context_precision", "llm_context_precision_without_reference"),
        ]:
            if not _HAS_CTX_PRECISION and display_key == "context_precision":
                continue
            v = raw.get(raw_key)
            if v is not None and not (isinstance(v, float) and math.isnan(v)):
                out[display_key] = float(v)

        return out or None
    except Exception:
        return None
