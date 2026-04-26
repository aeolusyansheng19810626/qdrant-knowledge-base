import streamlit as st
from ingestion.loader import upload_document, client, ensure_collection
from retrieval.search import search
from evaluation.evaluator import run_evaluation
from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector
from config import COLLECTION_NAME

st.set_page_config(page_title="AI 文档知识库", layout="centered")
st.title("📚 AI 技术文档知识库")

# 初始化或检查集合与索引
ensure_collection()

# ── 评估分数渲染 ───────────────────────────────────────────
_EVAL_LABELS = {
    "faithfulness": "忠实度",
    "answer_relevancy": "回答相关性",
    "context_precision": "检索精度",
}

def _render_eval_scores(scores: dict):
    cols = st.columns(max(len(scores), 1))
    for col, (key, val) in zip(cols, scores.items()):
        label = _EVAL_LABELS.get(key, key)
        color = "green" if val >= 0.8 else "orange" if val >= 0.5 else "red"
        col.markdown(f"**{label}**")
        col.markdown(f":{color}[**{val:.3f}**]")

# ── 侧边栏：管理文档 ──────────────────────────────────────
with st.sidebar:
    st.header("上传文档")
    uploaded_files = st.file_uploader(
        "选择 PDF 或 Markdown 文件（可多选）",
        type=["pdf", "md"],
        accept_multiple_files=True,
    )
    framework = st.text_input("框架名称", placeholder="例如：LangChain、Qdrant、Ollama")
    doc_type = st.selectbox("文档类型", ["教程", "API文档", "changelog", "其他"])

    if st.button("上传", use_container_width=True):
        if not uploaded_files:
            st.warning("请先选择文件")
        elif not framework:
            st.warning("请输入框架名称")
        else:
            for f in uploaded_files:
                with st.spinner(f"正在处理 {f.name}..."):
                    count = upload_document(f, framework, doc_type)
                    st.success(f"{f.name} 上传完成，共 {count} 个片段")
            st.rerun()

    st.divider()
    st.header("已上传文档")

    try:
        results, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            with_payload=True,
            limit=1000,
        )
        filenames = sorted(list({r.payload["filename"] for r in results if "filename" in r.payload}))

        if not filenames:
            st.info("知识库中暂无文档")
        else:
            for fname in filenames:
                col_name, col_del = st.columns([0.7, 0.3])
                col_name.write(f"📄 {fname}")
                if col_del.button("删除", key=f"del_{fname}", type="secondary"):
                    try:
                        with st.spinner(f"正在删除 {fname}..."):
                            client.delete(
                                collection_name=COLLECTION_NAME,
                                points_selector=FilterSelector(
                                    filter=Filter(
                                        must=[FieldCondition(key="filename", match=MatchValue(value=fname))]
                                    )
                                )
                            )
                            st.success(f"已删除 {fname}")
                            st.rerun()
                    except Exception as e:
                        st.error(f"删除失败: {e}")
    except Exception as e:
        st.error(f"加载文档列表失败: {e}")

# ── 主区域：问答 ──────────────────────────────────────────
st.subheader("🔍 文档问答")

col1, col2 = st.columns(2)
with col1:
    filter_framework = st.text_input("过滤框架", placeholder="留空则搜索全部")
with col2:
    filter_doc_type = st.selectbox("过滤文档类型", ["全部", "教程", "API文档", "changelog", "其他"])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 展示历史聊天记录
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            with st.expander("📎 来源文档"):
                for s in msg["sources"]:
                    st.markdown(f"**{s['framework']}** / {s['doc_type']} — `{s['filename']}` (chunk {s['chunk_index']}, score: {s['score']})")
                    st.caption(s["text"])
        if msg.get("eval_scores"):
            with st.expander("📊 RAGAS 评估"):
                _render_eval_scores(msg["eval_scores"])

# 输入框
if query := st.chat_input("用中文提问，例如：LangGraph 怎么定义节点？"):
    with st.chat_message("user"):
        st.markdown(query)
    st.session_state.chat_history.append({"role": "user", "content": query})

    with st.chat_message("assistant"):
        with st.spinner("搜索中..."):
            answer, sources = search(
                query,
                framework=filter_framework if filter_framework else None,
                doc_type=filter_doc_type,
            )
        st.markdown(answer)
        if sources:
            with st.expander("📎 来源文档"):
                for s in sources:
                    st.markdown(f"**{s['framework']}** / {s['doc_type']} — `{s['filename']}` (chunk {s['chunk_index']}, score: {s['score']})")
                    st.caption(s["text"])

        # 后台评估（在回答显示后运行，用户可见"评估中..."状态）
        eval_scores = None
        contexts = [s["text_full"] for s in sources] if sources else []
        with st.status("📊 RAGAS 评估中...", expanded=False) as eval_status:
            eval_scores = run_evaluation(query, answer, contexts)
            if eval_scores:
                _render_eval_scores(eval_scores)
                eval_status.update(label="📊 RAGAS 评估", state="complete", expanded=False)
            else:
                st.warning("评估失败，请检查 API 连接或上下文是否为空")
                eval_status.update(label="📊 RAGAS 评估（失败）", state="error", expanded=False)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "eval_scores": eval_scores,
    })
