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

# 📚 AI技術ドキュメント ナレッジベース

RAG（検索拡張生成）アーキテクチャに基づくAI技術ドキュメント質問応答システムです。PDFとMarkdownドキュメントのアップロードに対応し、ハイブリッド検索 + Rerankerによる高精度な関連コンテンツの取得、LLMによる回答生成を実現します。

---

## ✨ 主な機能

- **複数フォーマット対応**：PDFとMarkdown（`.md`）ファイルに対応
- **ハイブリッド検索**：セマンティックベクトル（`BAAI/bge-m3`）とキーワードベクトル（`BM25`）を併用し、RRFアルゴリズムで結果を統合。意味理解と正確なマッチングを両立
- **Rerankerによる再ランキング**：初期検索のTop-20候補に対し、`BAAI/bge-reranker-v2-m3` Cross-Encoderで精密なランキングを実施し、最も関連性の高いTop-5を抽出
- **メタデータフィルタ**：フレームワーク名（LangChain、Qdrantなど）とドキュメント種別（チュートリアル、APIドキュメントなど）による絞り込み検索に対応
- **ドキュメント管理**：サイドバーにアップロード済みドキュメント一覧をリアルタイム表示。ファイル単位で関連データを一括削除可能
- **出典情報の表示**：各回答に出典ドキュメント情報（ファイル名、チャンクインデックス、関連性スコア、テキスト要約）を付与
- **RAGAS自動評価**：質問応答ごとにRAGAS評価を自動実行。回答下部に忠実度・回答関連性・検索精度の3指標を折りたたみ表示（0〜1点、色分け表示）
- **多言語インターフェース**：簡体字中国語 / English / 日本語の3言語に対応。右上でワンクリック切替

---

## 🏗️ 技術アーキテクチャ

```
qdrant-knowledge-base/
├── app.py                  # Streamlitメインアプリ（アップロード、質問応答、ドキュメント管理UI）
├── config.py               # 設定管理（API Key、モデル名、コレクション名）
├── ingestion/
│   └── loader.py           # ドキュメント処理と登録（解析、分割、ベクトル化、保存）
├── retrieval/
│   └── search.py           # 検索と質問応答（ハイブリッド検索、Reranker、LLM生成）
├── evaluation/
│   └── evaluator.py        # RAGAS評価（忠実度、回答関連性、検索精度）
├── requirements.txt
└── .env                    # 環境変数（バージョン管理対象外）
```

### コア技術スタック

| コンポーネント | 技術 |
|---|---|
| フロントエンドUI | Streamlit |
| ベクトルデータベース | Qdrant Cloud |
| 密ベクトルモデル | `BAAI/bge-m3`（1024次元、コサイン類似度） |
| 疎ベクトルモデル | `Qdrant/bm25`（via fastembed） |
| 融合アルゴリズム | RRF（逆数順位融合） |
| 再ランキングモデル | `BAAI/bge-reranker-v2-m3` |
| 大規模言語モデル | `meta-llama/llama-4-scout-17b-16e-instruct`（via Groq） |
| RAG評価フレームワーク | RAGAS（`Faithfulness` / `AnswerRelevancy` / `LLMContextPrecisionWithoutReference`） |

---

## 🚀 クイックスタート

### 1. 環境準備

**Python 3.10以上** を推奨。仮想環境の使用を推奨します：

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

> **注意**：初回実行時に`bge-m3`（約570MB）と`bge-reranker-v2-m3`（約570MB）のモデルが自動ダウンロードされます。ネットワーク接続を確認してください。

### 3. 環境変数の設定

プロジェクトルートディレクトリに`.env`ファイルを作成：

```env
GROQ_API_KEY=your_groq_api_key
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your_qdrant_api_key
```

- **Groq API Key**：[https://console.groq.com](https://console.groq.com)で無料取得可能
- **Qdrant**：[https://cloud.qdrant.io](https://cloud.qdrant.io)で無料クラスタを作成し、URLとKeyを取得

### 4. アプリケーション起動

```bash
streamlit run app.py
```

---

## 📖 使用方法

### ドキュメントのアップロード

1. 左側のサイドバーで **「PDFまたはMarkdownファイルを選択」** をクリックしてドキュメントをアップロード（複数選択可）
2. **フレームワーク名**を入力（例：`LangChain`、`Qdrant`、`Ollama`）
3. **ドキュメント種別**を選択（チュートリアル / APIドキュメント / changelog / その他）
4. **「アップロード」** ボタンをクリックし、処理完了を待つ

### ドキュメントへの質問

1. メインエリアでフレームワークとドキュメント種別による絞り込みが可能（空白の場合は全体を検索）
2. 下部の入力欄に質問を入力し、Enterで送信
3. システムがAI生成の回答を返し、**「📎 出典ドキュメント」** を展開すると検索された元のテキスト断片を確認可能
4. 回答下部に **「📊 RAGAS評価」** が自動表示（評価に約5〜10秒）。展開すると忠実度・回答関連性・検索精度の定量的スコアを確認可能

### ドキュメントの削除

サイドバーの **「アップロード済みドキュメント」** エリアで、対応するドキュメントの横にある **「削除」** ボタンをクリックすると、そのファイルのすべてのベクトルデータが削除されます。

---

## ⚙️ 設定について

すべてのコア設定は`config.py`に集約されています：

| 設定項目 | デフォルト値 | 説明 |
|---|---|---|
| `EMBEDDING_MODEL` | `BAAI/bge-m3` | 密ベクトルモデル |
| `LLM_MODEL` | `meta-llama/llama-4-scout-17b-16e-instruct` | 生成モデル |
| `COLLECTION_NAME` | `ai_docs` | Qdrantコレクション名 |
| `VECTOR_SIZE` | `1024` | ベクトル次元（bge-m3に対応） |

分割戦略は`ingestion/loader.py`で調整可能：

| パラメータ | デフォルト値 | 説明 |
|---|---|---|
| `chunk_size` | `8` | 各チャンクに含まれる文数 |
| `overlap` | `2` | 隣接チャンクの重複文数 |
| `batch_size` | `10` | Qdrantへの一括書き込みpoint数 |

---

## 🔍 検索フロー

```
ユーザーの質問
   │
   ├─ 密ベクトル生成（bge-m3）
   └─ 疎ベクトル生成（BM25）
         │
         ▼
   Qdrantハイブリッド検索（各Top-20を取得）
         │
         ▼
   RRF融合ソート → Top-20をマージ
         │
         ▼
   Reranker精密ランキング（bge-reranker-v2-m3）→ Top-5
         │
         ▼
   コンテキスト組み立て → Groq LLMで回答生成
         │
         ▼
   回答 + 出典ドキュメントを返す
         │
         ▼
   RAGAS評価（Faithfulness / AnswerRelevancy / ContextPrecision）
         │
         ▼
   評価スコアを折りたたみ表示（緑 ≥ 0.8 / 黄 ≥ 0.5 / 赤 < 0.5）
```

---

## 📝 ライセンス

MIT License

---

## 👤 作者

Built by [Sheng Yan](https://github.com/aeolusyansheng19810626)

プロジェクトリポジトリ：[GitHub](https://github.com/aeolusyansheng19810626/qdrant-knowledge-base)