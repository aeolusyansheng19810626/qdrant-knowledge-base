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

# 📚 AI 技術ﾄﾞｷｭﾒﾝﾄﾅﾚｯｼﾞﾍﾞｰｽ

RAG（検索拡張生成）ｱｰｷﾃｸﾁｬに基づく AI 技術ﾄﾞｷｭﾒﾝﾄ質問応答ｼｽﾃﾑ。PDF と Markdown ﾄﾞｷｭﾒﾝﾄのｱｯﾌﾟﾛｰﾄﾞをｻﾎﾟｰﾄし、ﾊｲﾌﾞﾘｯﾄﾞ検索 + Reranker による正確な関連ｺﾝﾃﾝﾂの取得、LLM による最終回答の生成を実現します。

---

## ✨ 機能特性

- **複数ﾌｫｰﾏｯﾄ対応**：PDF と Markdown (`.md`) ﾌｧｲﾙをｻﾎﾟｰﾄ。
- **ﾊｲﾌﾞﾘｯﾄﾞ検索**：意味ﾍﾞｸﾄﾙ（`BAAI/bge-m3`）とｷｰﾜｰﾄﾞﾍﾞｸﾄﾙ（`BM25`）を同時使用し、RRF ｱﾙｺﾞﾘｽﾞﾑで結果を融合。意味理解と正確なﾏｯﾁﾝｸﾞを両立。
- **Reranker 再順位付け**：初期検索の Top-20 候補に対し、`BAAI/bge-reranker-v2-m3` Cross-Encoder で精密な順位付けを行い、最も関連性の高い Top-5 を選出。
- **ﾒﾀﾃﾞｰﾀﾌｨﾙﾀ**：ﾌﾚｰﾑﾜｰｸ名（LangChain、Qdrant など）とﾄﾞｷｭﾒﾝﾄ種類（ﾁｭｰﾄﾘｱﾙ、API ﾄﾞｷｭﾒﾝﾄなど）による正確なﾌｨﾙﾀﾘﾝｸﾞをｻﾎﾟｰﾄ。
- **ﾄﾞｷｭﾒﾝﾄ管理**：ｻｲﾄﾞﾊﾞｰにｱｯﾌﾟﾛｰﾄﾞ済みﾄﾞｷｭﾒﾝﾄﾘｽﾄをﾘｱﾙﾀｲﾑ表示、ﾌｧｲﾙ単位で関連ﾃﾞｰﾀを一括削除可能。
- **出典表示**：各回答に出典ﾄﾞｷｭﾒﾝﾄ情報（ﾌｧｲﾙ名、ﾁｬﾝｸｲﾝﾃﾞｯｸｽ、関連性ｽｺｱ、ﾃｷｽﾄ要約）を添付。
- **RAGAS 自動評価**：各質問応答後に RAGAS 評価を自動実行、回答下部に忠実度・回答関連性・検索精度の 3 指標を折りたたみ表示（0–1 点、色分け表示）。
- **多言語ｲﾝﾀｰﾌｪｰｽ**：簡体字中国語 / English / 日本語の 3 言語をｻﾎﾟｰﾄ、右上でﾜﾝｸﾘｯｸ切替。

---

## 🏗️ 技術ｱｰｷﾃｸﾁｬ

```
qdrant-knowledge-base/
├── app.py                  # Streamlit ﾒｲﾝｱﾌﾟﾘ（ｱｯﾌﾟﾛｰﾄﾞ、質問応答、ﾄﾞｷｭﾒﾝﾄ管理 UI）
├── config.py               # 設定管理（API Key、ﾓﾃﾞﾙ名、ｺﾚｸｼｮﾝ名）
├── ingestion/
│   └── loader.py           # ﾄﾞｷｭﾒﾝﾄ処理と登録（解析、分割、ﾍﾞｸﾄﾙ化、保存）
├── retrieval/
│   └── search.py           # 検索と質問応答（ﾊｲﾌﾞﾘｯﾄﾞ検索、Reranker、LLM 生成）
├── evaluation/
│   └── evaluator.py        # RAGAS 評価（忠実度、回答関連性、検索精度）
├── requirements.txt
└── .env                    # 環境変数（ﾊﾞｰｼﾞｮﾝ管理に含めない）
```

### ｺｱ技術ｽﾀｯｸ

| ｺﾝﾎﾟｰﾈﾝﾄ | 技術 |
|---|---|
| ﾌﾛﾝﾄｴﾝﾄﾞ UI | Streamlit |
| ﾍﾞｸﾄﾙﾃﾞｰﾀﾍﾞｰｽ | Qdrant Cloud |
| 密ﾍﾞｸﾄﾙﾓﾃﾞﾙ | `BAAI/bge-m3`（1024 次元、ｺｻｲﾝ類似度） |
| 疎ﾍﾞｸﾄﾙﾓﾃﾞﾙ | `Qdrant/bm25`（via fastembed） |
| 融合ｱﾙｺﾞﾘｽﾞﾑ | RRF（逆数順位融合） |
| 再順位付けﾓﾃﾞﾙ | `BAAI/bge-reranker-v2-m3` |
| 大規模言語ﾓﾃﾞﾙ | `meta-llama/llama-4-scout-17b-16e-instruct`（via Groq） |
| RAG 評価ﾌﾚｰﾑﾜｰｸ | RAGAS（`Faithfulness` / `AnswerRelevancy` / `LLMContextPrecisionWithoutReference`） |

---

## 🚀 ｸｲｯｸｽﾀｰﾄ

### 1. 環境準備

**Python 3.10+** 仮想環境の使用を推奨：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. 依存関係のｲﾝｽﾄｰﾙ

```bash
pip install -r requirements.txt
```

> **注意**：初回実行時に `bge-m3`（約 570MB）と `bge-reranker-v2-m3`（約 570MB）ﾓﾃﾞﾙが自動ﾀﾞｳﾝﾛｰﾄﾞされます。ﾈｯﾄﾜｰｸ接続を確認してください。

### 3. 環境変数の設定

ﾌﾟﾛｼﾞｪｸﾄﾙｰﾄﾃﾞｨﾚｸﾄﾘに `.env` ﾌｧｲﾙを作成：

```env
GROQ_API_KEY=your_groq_api_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
```

- **Groq API Key**：[https://console.groq.com](https://console.groq.com) で無料取得。
- **Qdrant**：[https://cloud.qdrant.io](https://cloud.qdrant.io) で無料ｸﾗｽﾀを作成し URL と Key を取得。

### 4. ｱﾌﾟﾘｹｰｼｮﾝ起動

```bash
streamlit run app.py
```

---

## 📖 使用方法

### ﾄﾞｷｭﾒﾝﾄのｱｯﾌﾟﾛｰﾄﾞ

1. 左側のｻｲﾄﾞﾊﾞｰで **"PDF または Markdown ﾌｧｲﾙを選択"** をｸﾘｯｸしてﾄﾞｷｭﾒﾝﾄをｱｯﾌﾟﾛｰﾄﾞ（複数選択可）。
2. **ﾌﾚｰﾑﾜｰｸ名**を入力（例：`LangChain`、`Qdrant`、`Ollama`）。
3. **ﾄﾞｷｭﾒﾝﾄ種類**を選択（ﾁｭｰﾄﾘｱﾙ / API ﾄﾞｷｭﾒﾝﾄ / changelog / その他）。
4. **"ｱｯﾌﾟﾛｰﾄﾞ"** ﾎﾞﾀﾝをｸﾘｯｸし、処理完了を待つ。

### ﾄﾞｷｭﾒﾝﾄ質問応答

1. ﾒｲﾝｴﾘｱでﾌﾚｰﾑﾜｰｸとﾄﾞｷｭﾒﾝﾄ種類によるﾌｨﾙﾀﾘﾝｸﾞが可能（空白の場合は全体を検索）。
2. 下部の入力欄に質問を入力し、Enter で送信。
3. ｼｽﾃﾑが AI 生成の回答を返し、**"📎 出典ﾄﾞｷｭﾒﾝﾄ"** を展開すると検索された元のﾃｷｽﾄ断片を確認可能。
4. 回答下部に **"📊 RAGAS 評価"** が自動表示（評価に約 5–10 秒）、展開すると忠実度・回答関連性・検索精度の定量的ｽｺｱを確認可能。

### ﾄﾞｷｭﾒﾝﾄの削除

ｻｲﾄﾞﾊﾞｰの **"ｱｯﾌﾟﾛｰﾄﾞ済みﾄﾞｷｭﾒﾝﾄ"** ｴﾘｱで、対応するﾄﾞｷｭﾒﾝﾄの横にある **"削除"** ﾎﾞﾀﾝをｸﾘｯｸすると、そのﾌｧｲﾙのすべてのﾍﾞｸﾄﾙﾃﾞｰﾀが削除されます。

---

## ⚙️ 設定説明

すべてのｺｱ設定は `config.py` に集約：

| 設定項目 | ﾃﾞﾌｫﾙﾄ値 | 説明 |
|---|---|---|
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | 密ﾍﾞｸﾄﾙﾓﾃﾞﾙ |
| `LLM_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` | 生成ﾓﾃﾞﾙ |
| `COLLECTION_NAME` | `ai_docs` | Qdrant ｺﾚｸｼｮﾝ名 |
| `VECTOR_SIZE` | `1024` | ﾍﾞｸﾄﾙ次元（bge-m3 に対応） |

分割戦略は `ingestion/loader.py` で調整：

| ﾊﾟﾗﾒｰﾀ | ﾃﾞﾌｫﾙﾄ値 | 説明 |
|---|---|---|
| `chunk_size` | `8` | 各ﾁｬﾝｸに含まれる文数 |
| `overlap` | `2` | 隣接ﾁｬﾝｸの重複文数 |
| `batch_size` | `10` | Qdrant への一括書き込み point 数 |

---

## 🔍 検索ﾌﾛｰ

```
ﾕｰｻﾞｰの質問
   │
   ├─ 密ﾍﾞｸﾄﾙ生成（bge-m3）
   └─ 疎ﾍﾞｸﾄﾙ生成（BM25）
         │
         ▼
   Qdrant ﾊｲﾌﾞﾘｯﾄﾞ検索（各 Top-20 を取得）
         │
         ▼
   RRF 融合ｿｰﾄ → Top-20 をﾏｰｼﾞ
         │
         ▼
   Reranker 精密順位付け（bge-reranker-v2-m3）→ Top-5
         │
         ▼
   ｺﾝﾃｷｽﾄ組み立て → Groq LLM で回答生成
         │
         ▼
   回答 + 出典ﾄﾞｷｭﾒﾝﾄを返す
         │
         ▼
   RAGAS 評価（Faithfulness / AnswerRelevancy / ContextPrecision）
         │
         ▼
   評価ｽｺｱを折りたたみ表示（緑 ≥ 0.8 / 黄 ≥ 0.5 / 赤 < 0.5）
```

---

## 📝 ﾗｲｾﾝｽ

MIT License

---

## 👤 作者

Built by [Sheng Yan](https://github.com/aeolusyansheng19810626)

ﾌﾟﾛｼﾞｪｸﾄﾘﾎﾟｼﾞﾄﾘ：[GitHub](https://github.com/aeolusyansheng19810626/qdrant-knowledge-base)