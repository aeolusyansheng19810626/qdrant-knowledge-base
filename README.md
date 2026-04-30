---
title: Qdrant Knowledge Base
emoji: 📚
colorFrom: green
colorTo: blue
sdk: streamlit
sdk_version: "1.56.0"
python_version: "3.11"
app_file: app.py
pinned: false
---

# 📚 AI 技术文档知识库

基于 RAG（检索增强生成）架构的 AI 技术文档问答系统。支持上传 PDF 和 Markdown 文档，通过混合检索 + Reranker 精准召回相关内容，由 LLM 生成最终答案。

---

## ✨ 功能特性

- **多格式上传**：支持 PDF 和 Markdown (`.md`) 文件。
- **混合检索**：同时使用语义向量（`BAAI/bge-m3`）和关键词向量（`BM25`），通过 RRF 算法融合结果，兼顾语义理解与精确匹配。
- **Reranker 重排**：对初步召回的 Top-20 候选项，使用 `BAAI/bge-reranker-v2-m3` Cross-Encoder 精排，选出最相关的 Top-5。
- **元数据过滤**：支持按框架名称（如 LangChain、Qdrant）和文档类型（教程、API文档等）进行精确过滤。
- **文档管理**：侧边栏实时展示已上传文档列表，支持一键按文件删除所有关联数据。
- **溯源展示**：每次回答均附带来源文档信息（文件名、分块索引、相关性得分、文本摘要）。
- **RAGAS 自动评估**：每次问答后自动运行 RAGAS 评估，在回答下方折叠展示忠实度、回答相关性、检索精度三项指标（0–1 分，颜色标注）。
- **多语言界面**：支持简体中文 / English / 日本語 三种界面语言，右上角一键切换。

---

## 🏗️ 技术架构

```
qdrant-knowledge-base/
├── app.py                  # Streamlit 主应用（上传、问答、文档管理界面）
├── config.py               # 配置管理（API Key、模型名称、集合名称）
├── ingestion/
│   └── loader.py           # 文档处理与入库（解析、分块、向量化、存储）
├── retrieval/
│   └── search.py           # 检索与问答（混合检索、Reranker、LLM 生成）
├── evaluation/
│   └── evaluator.py        # RAGAS 评估（忠实度、回答相关性、检索精度）
├── requirements.txt
└── .env                    # 环境变量（不提交到版本控制）
```

### 核心技术栈

| 组件 | 技术 |
|---|---|
| 前端界面 | Streamlit |
| 向量数据库 | Qdrant Cloud |
| 稠密向量模型 | `BAAI/bge-m3`（1024 维，余弦相似度） |
| 稀疏向量模型 | `Qdrant/bm25`（via fastembed） |
| 融合算法 | RRF（倒数排名融合） |
| 重排序模型 | `BAAI/bge-reranker-v2-m3` |
| 大语言模型 | `meta-llama/llama-4-scout-17b-16e-instruct`（via Groq） |
| RAG 评估框架 | RAGAS（`Faithfulness` / `AnswerRelevancy` / `LLMContextPrecisionWithoutReference`） |

---

## 🚀 快速开始

### 1. 环境准备

**Python 3.10+** 推荐使用虚拟环境：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

> **注意**：首次运行时会自动下载 `bge-m3`（约 570MB）和 `bge-reranker-v2-m3`（约 570MB）模型，请确保网络畅通。

### 3. 配置环境变量

在项目根目录创建 `.env` 文件：

```env
GROQ_API_KEY=your_groq_api_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
```

- **Groq API Key**：在 [https://console.groq.com](https://console.groq.com) 免费获取。
- **Qdrant**：在 [https://cloud.qdrant.io](https://cloud.qdrant.io) 创建免费集群获取 URL 和 Key。

### 4. 启动应用

```bash
streamlit run app.py
```

---

## 📖 使用说明

### 上传文档

1. 在左侧侧边栏点击 **"选择 PDF 或 Markdown 文件"** 上传文档（支持多选）。
2. 填写 **框架名称**（如：`LangChain`、`Qdrant`、`Ollama`）。
3. 选择 **文档类型**（教程 / API文档 / changelog / 其他）。
4. 点击 **"上传"** 按钮，等待处理完成。

### 文档问答

1. 在主区域可选择按框架和文档类型进行过滤（留空则搜索全库）。
2. 在底部输入框输入问题，按回车提交。
3. 系统会返回 AI 生成的答案，点击展开 **"📎 来源文档"** 可查看检索到的原始文本片段。
4. 答案下方会自动显示 **"📊 RAGAS 评估"**（评估中约需 5–10 秒），展开后可查看忠实度、回答相关性、检索精度的量化分数。

### 删除文档

在侧边栏 **"已上传文档"** 区域，点击对应文档旁的 **"删除"** 按钮，即可删除该文件的所有向量数据。

---

## ⚙️ 配置说明

所有核心配置集中在 `config.py`：

| 配置项 | 默认值 | 说明 |
|---|---|---|
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | 稠密向量模型 |
| `LLM_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` | 生成模型 |
| `COLLECTION_NAME` | `ai_docs` | Qdrant 集合名称 |
| `VECTOR_SIZE` | `1024` | 向量维度（与 bge-m3 对应） |

分块策略在 `ingestion/loader.py` 中调整：

| 参数 | 默认值 | 说明 |
|---|---|---|
| `chunk_size` | `8` | 每个分块包含的句子数 |
| `overlap` | `2` | 相邻分块的重叠句子数 |
| `batch_size` | `10` | 每批写入 Qdrant 的 point 数量 |

---

## 🔍 检索流程

```
用户提问
   │
   ├─ 生成稠密向量（bge-m3）
   └─ 生成稀疏向量（BM25）
         │
         ▼
   Qdrant 混合检索（各召回 Top-20）
         │
         ▼
   RRF 融合排序 → 合并 Top-20
         │
         ▼
   Reranker 精排（bge-reranker-v2-m3）→ Top-5
         │
         ▼
   组装上下文 → Groq LLM 生成答案
         │
         ▼
   返回答案 + 来源文档
         │
         ▼
   RAGAS 评估（Faithfulness / AnswerRelevancy / ContextPrecision）
         │
         ▼
   折叠展示评估分数（绿 ≥ 0.8 / 黄 ≥ 0.5 / 红 < 0.5）
```
