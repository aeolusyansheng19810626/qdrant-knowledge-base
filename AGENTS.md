# AGENTS.md — AI Agent 快速上手指南

> 本文件专为 AI coding agent 设计。新 session 开始时，请先读此文件，再按需读取相关源文件。

---

## 项目一句话描述

基于 RAG 架构的 AI 技术文档问答系统：上传 PDF / Markdown → 混合检索（语义 + 关键词）→ Reranker 精排 → LLM 生成答案。

---

## 目录结构

```
qdrant-knowledge-base/
├── app.py                  # Streamlit 主入口，含侧边栏上传/删除 UI 和聊天区域
├── config.py               # 所有常量（API Key、模型名、集合名、向量维度）
├── ingestion/
│   └── loader.py           # 文档处理管道：解析 → 分块 → 双向量化 → 写入 Qdrant
├── retrieval/
│   └── search.py           # 检索管道：混合检索 → RRF 融合 → Reranker → LLM 生成
├── requirements.txt
├── .env                    # 本地密钥（不提交）
├── README.md               # 项目文档（面向人类）
└── AGENTS.md               # 本文件（面向 AI agent）
```

---

## 关键函数速查

### `ingestion/loader.py`

| 函数 | 签名 | 说明 |
|---|---|---|
| `ensure_collection()` | `() -> None` | 创建 Qdrant 集合和 payload 索引（幂等，可重复调用） |
| `extract_text()` | `(file) -> str` | 支持 `.pdf` 和 `.md`，返回纯文本 |
| `split_into_sentences()` | `(text: str) -> list[str]` | 按句子边界切分，过滤短句（< 20字符） |
| `chunk_by_sentences()` | `(sentences, chunk_size=8, overlap=2) -> list[str]` | 带重叠的句子级分块 |
| `upload_document()` | `(file, framework: str, doc_type: str) -> int` | 完整入库管道，返回写入的 chunk 数量 |

### `retrieval/search.py`

| 函数 | 签名 | 说明 |
|---|---|---|
| `build_filter()` | `(framework=None, doc_type=None) -> Filter \| None` | 构造 Qdrant payload 过滤条件 |
| `search()` | `(query: str, framework=None, doc_type=None, top_k=5) -> tuple[str, list[dict]]` | 完整检索管道，返回 (LLM回答, 来源列表) |

### `app.py`

无独立函数，为 Streamlit 脚本式代码。关键逻辑位置：
- **上传逻辑**：`st.button("上传")` 回调块
- **文档列表 + 删除**：`st.header("已上传文档")` 块，使用 `client.scroll` + `client.delete`
- **问答**：`st.chat_input` 触发，调用 `search()`

---

## 数据模型

每个存入 Qdrant 的 point 结构如下：

```python
PointStruct(
    id=str(uuid.uuid4()),
    vector={
        "dense": List[float],        # bge-m3 输出，1024 维
        "sparse": SparseVector(...), # BM25 稀疏向量
    },
    payload={
        "text": str,          # 原始文本块
        "framework": str,     # 用户填写，如 "LangChain"
        "doc_type": str,      # 用户选择，如 "API文档"
        "filename": str,      # 原始文件名，用于删除时过滤
        "chunk_index": int,   # 该 chunk 在文件中的序号
    }
)
```

**已建立 Payload 索引的字段**（可用于 Filter）：`framework`、`doc_type`、`filename`

---

## 重要约定

- **模型加载**：所有模型（dense embedder、sparse embedder、reranker）均通过 `@st.cache_resource` 缓存，**不要**在函数内部直接实例化模型，应调用对应的 `get_xxx()` 函数。
- **集合初始化**：`ensure_collection()` 是幂等的，在 `app.py` 启动时调用一次，在 `upload_document()` 内也会调用一次。修改集合结构后需手动在 Qdrant 控制台删除旧集合。
- **删除操作**：通过 `filename` 字段过滤删除，依赖 `filename` 的 payload 索引，**不要**移除该索引。
- **分块参数**：`chunk_size=8, overlap=2`，如需调整请同时评估对检索召回率的影响。

---

## 常见任务指引

### 新增支持的文件格式
→ 修改 `ingestion/loader.py` 中的 `extract_text()` 函数，添加新的 `elif` 分支  
→ 修改 `app.py` 中 `st.file_uploader` 的 `type=[...]` 列表

### 修改检索召回数量
→ 修改 `retrieval/search.py` 中 `Prefetch` 的 `limit` 参数（当前为 20）  
→ 修改 `FusionQuery` 后的 `limit` 参数

### 修改 Reranker 最终返回数量
→ 修改 `search()` 函数的 `top_k` 参数默认值（当前为 5）

### 更换 LLM 模型
→ 修改 `config.py` 中的 `LLM_MODEL` 字符串（需为 Groq 支持的模型 ID）

### 更换 Embedding 模型
→ 修改 `config.py` 中的 `EMBEDDING_MODEL` 和 `VECTOR_SIZE`  
→ **必须**在 Qdrant 控制台删除旧集合，否则维度不匹配会报错

### 新增 payload 过滤字段
→ 在 `ingestion/loader.py` 的 `ensure_collection()` 中添加 `create_payload_index`  
→ 在 `retrieval/search.py` 的 `build_filter()` 中添加对应的 `FieldCondition`  
→ 在 `ingestion/loader.py` 的 `upload_document()` 的 `payload` 字典中添加字段

---

## 环境变量（`.env`）

| 变量名 | 用途 |
|---|---|
| `GROQ_API_KEY` | Groq LLM API 密钥 |
| `QDRANT_URL` | Qdrant 集群地址 |
| `QDRANT_API_KEY` | Qdrant API 密钥 |

---

## 已知临时代码

- `retrieval/search.py` 第 89-90 行：有两行 `print` 调试语句用于对比 rerank 前后顺序，正式上线前需删除。
