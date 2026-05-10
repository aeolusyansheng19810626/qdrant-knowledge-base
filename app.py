import streamlit as st
from ingestion.loader import upload_document, client, ensure_collection
from retrieval.search import search
from evaluation.evaluator import run_evaluation
from qdrant_client.models import Filter, FieldCondition, MatchValue, FilterSelector
from config import COLLECTION_NAME

st.set_page_config(page_title="AI 技术文档知识库", layout="wide", initial_sidebar_state="expanded")

# 言語状態の初期化
if "lang" not in st.session_state:
    st.session_state.lang = "en"

I18N = {
    "zh": {
        "title": "AI 技术文档知识库",
        "subtitle": "基于 RAG 的文档问答 · 检索增强生成",
        "docs_count": "向量库 · {} 文档",
        "qa_title": "文档问答",
        "ask": "Ask",
        "framework": "框架",
        "framework_ph": "留空则搜索全部",
        "doc_type": "文档类型",
        "type_all": "全部",
        "upload": "上传文档",
        "drop_text": "拖拽或点击上传",
        "drop_meta": "PDF · MD · 单文件 ≤ 200MB",
        "fw_name": "框架名称",
        "fw_name_ph": "例如：LangChain、Qdrant",
        "add_btn": "添加到知识库",
        "uploaded": "已上传文档",
        "ready": "向量索引 · 已就绪",
        "error": "向量索引 · 连接失败",
        "retry": "🔄 重试连接",
        "sidebar_kb": "知识库",
        "sidebar_kb_en": "KNOWLEDGE BASE",
        "chat_ph": "用中文提问，例如：LangGraph 怎么定义节点？",
        "searching": "搜索中...",
        "src_docs": "来源文档",
        "eval_scores": "RAGAS 评估分数",
        "click_fold": "点击展开 / 收起",
        "comprehensive": "综合 {}",
        "faithfulness": "Faithfulness · 忠实度",
        "relevancy": "Answer Relevancy · 相关性",
        "precision": "Context Precision · 准确度",
        "related": "相关度 {}%",
        "paragraph": "第 {} 段",
        "type_tutorial": "教程",
        "type_api": "API文档",
        "type_other": "其他",
        "empty_kb": "知识库中暂无文档"
    },
    "en": {
        "title": "AI Tech Docs Knowledge Base",
        "subtitle": "RAG-based Document QA & Retrieval-Augmented Generation",
        "docs_count": "Vector DB · {} Docs",
        "qa_title": "Document QA",
        "ask": "Ask",
        "framework": "Framework",
        "framework_ph": "Leave blank to search all",
        "doc_type": "Doc Type",
        "type_all": "All",
        "upload": "Upload Document",
        "drop_text": "Drag and drop or click to upload",
        "drop_meta": "PDF · MD · Single file ≤ 200MB",
        "fw_name": "Framework Name",
        "fw_name_ph": "e.g., LangChain, Qdrant",
        "add_btn": "Add to Knowledge Base",
        "uploaded": "Uploaded Documents",
        "ready": "Vector Index · Ready",
        "error": "Vector Index · Connection Failed",
        "retry": "🔄 Retry Connection",
        "sidebar_kb": "Knowledge Base",
        "sidebar_kb_en": "LIBRARY",
        "chat_ph": "Ask a question in English, e.g., How to define a node in LangGraph?",
        "searching": "Searching...",
        "src_docs": "Source Documents",
        "eval_scores": "RAGAS Evaluation Scores",
        "click_fold": "Click to expand / collapse",
        "comprehensive": "Overall {}",
        "faithfulness": "Faithfulness",
        "relevancy": "Answer Relevancy",
        "precision": "Context Precision",
        "related": "Relevance {}%",
        "paragraph": "Paragraph {}",
        "type_tutorial": "Tutorial",
        "type_api": "API Docs",
        "type_other": "Other",
        "empty_kb": "Knowledge base is empty"
    },
    "ja": {
        "title": "AI 技術ﾄﾞｷｭﾒﾝﾄﾅﾚｯｼﾞﾍﾞｰｽ",
        "subtitle": "RAG ﾍﾞｰｽのﾄﾞｷｭﾒﾝﾄ QA・検索拡張生成",
        "docs_count": "ﾍﾞｸﾄﾙ DB · {} ﾄﾞｷｭﾒﾝﾄ",
        "qa_title": "ﾄﾞｷｭﾒﾝﾄ QA",
        "ask": "Ask",
        "framework": "ﾌﾚｰﾑﾜｰｸ",
        "framework_ph": "空白ですべて検索",
        "doc_type": "ﾄﾞｷｭﾒﾝﾄの種類",
        "type_all": "すべて",
        "upload": "ﾄﾞｷｭﾒﾝﾄをｱｯﾌﾟﾛｰﾄﾞ",
        "drop_text": "ﾄﾞﾗｯｸﾞ&ﾄﾞﾛｯﾌﾟまたはｸﾘｯｸでｱｯﾌﾟﾛｰﾄﾞ",
        "drop_meta": "PDF · MD · 1ﾌｧｲﾙ ≤ 200MB",
        "fw_name": "ﾌﾚｰﾑﾜｰｸ名",
        "fw_name_ph": "例：LangChain、Qdrant",
        "add_btn": "ﾅﾚｯｼﾞﾍﾞｰｽに追加",
        "uploaded": "ｱｯﾌﾟﾛｰﾄﾞ済みﾄﾞｷｭﾒﾝﾄ",
        "ready": "ﾍﾞｸﾄﾙｲﾝﾃﾞｯｸｽ · 準備完了",
        "error": "ﾍﾞｸﾄﾙｲﾝﾃﾞｯｸｽ · 接続失敗",
        "retry": "🔄 再接続",
        "sidebar_kb": "ﾅﾚｯｼﾞﾍﾞｰｽ",
        "sidebar_kb_en": "KNOWLEDGE BASE",
        "chat_ph": "日本語で質問してください、例：LangGraph でﾉｰﾄﾞを定義するには？",
        "searching": "検索中...",
        "src_docs": "ｿｰｽﾄﾞｷｭﾒﾝﾄ",
        "eval_scores": "RAGAS 評価ｽｺｱ",
        "click_fold": "ｸﾘｯｸして展開 / 折りたたむ",
        "comprehensive": "総合 {}",
        "faithfulness": "Faithfulness · 忠実度",
        "relevancy": "Answer Relevancy · 関連性",
        "precision": "Context Precision · 精度",
        "related": "関連度 {}%",
        "paragraph": "第 {} 段落",
        "type_tutorial": "ﾁｭｰﾄﾘｱﾙ",
        "type_api": "API ﾄﾞｷｭﾒﾝﾄ",
        "type_other": "その他",
        "empty_kb": "ﾅﾚｯｼﾞﾍﾞｰｽは空です"
    }
}
t = I18N[st.session_state.lang]

# コレクションとインデックスの初期化・確認
if "index_status" not in st.session_state:
    try:
        ensure_collection()
        st.session_state.index_status = "ready"
        st.session_state.error_msg = None
    except Exception as e:
        st.session_state.index_status = "error"
        st.session_state.error_msg = str(e)

styles_css = """
/* ====== デザイントークン ====== */
:root {
  --bg:        #F7F7FB;
  --bg-2:      #EFEFF5;
  --surface:   #FFFFFF;
  --line:      #E8E8F0;
  --line-2:    #DEDEE8;
  --line-3:    #C9C9D6;
  --sidebar-bg:#F8F5FF;
  --fg:        #0F0F1A;
  --fg-2:      #2E2E40;
  --fg-3:      #5E5E73;
  --fg-4:      #9494A8;
  --brand:     #4338CA;
  --brand-2:   #6D28D9;
  --brand-3:   #8B5CF6;
  --brand-4:   #A78BFA;
  --accent:    #7C3AED;
  --accent-2:  #5B21B6;
  --electric:  #6366F1;
  --brand-50:  #F3F0FF;
  --brand-100: #E5DEFF;
  --brand-200: #C9BCFF;
  --brand-300: #A78BFA;
  --grad-1: linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #A855F7 100%);
  --grad-2: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
  --grad-aurora: linear-gradient(120deg, #4338CA 0%, #5B21B6 30%, #6D28D9 55%, #7C3AED 80%, #8B5CF6 100%);
  --grad-soft: linear-gradient(135deg, #F3F0FF 0%, #FAF5FF 100%);
  --green:     #10B981;
  --green-50:  #ECFDF5;
  --amber:     #F59E0B;
  --amber-50:  #FFFBEB;
  --rose:      #F43F5E;
  --rose-50:   #FFF1F2;
  --r-sm: 6px;
  --r-md: 10px;
  --r-lg: 14px;
  --r-xl: 18px;
  --shadow-sm: 0 1px 2px rgba(24,24,27,.04), 0 0 0 1px rgba(24,24,27,.04);
  --shadow-md: 0 4px 16px rgba(24,24,27,.06), 0 0 0 1px rgba(24,24,27,.05);
  --shadow-lg: 0 16px 40px rgba(24,24,27,.08), 0 0 0 1px rgba(24,24,27,.05);
}
* { box-sizing: border-box; }
body {
  font-family: "Inter","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif;
  font-size: 14px; color: var(--fg); background: var(--bg);
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
}
button { font-family: inherit; cursor: pointer; }
input, textarea, select { font-family: inherit; font-size: inherit; color: inherit; }
.brand-title {
  font-size: 15px; font-weight: 700;
  background: var(--grad-aurora);
  -webkit-background-clip: text; background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: .01em;
}
.brand-sub { font-size: 11px; color: var(--fg-4); margin-top: 2px; letter-spacing: .04em; text-transform: uppercase; }
.side-label { font-size: 11px; font-weight: 600; letter-spacing: .08em; text-transform: uppercase; color: var(--fg-4); display: flex; align-items: center; gap: 8px; }
.foot-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); box-shadow: 0 0 0 3px var(--green-50); }
.side-foot { margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--line); font-size: 11px; color: var(--fg-3); display: flex; align-items: center; gap: 8px; }
.side-author { margin-top: 16px; padding-top: 12px; font-size: 11px; color: var(--fg-4); text-align: center; }
.side-author a { color: var(--brand); text-decoration: none; font-weight: 500; }
.side-author a:hover { color: var(--brand-2); text-decoration: underline; }
.doc-row { background: var(--surface); border: 1px solid var(--line); border-radius: var(--r-md); padding: 12px; margin-bottom: 8px; transition: all .15s; }
.doc-row:hover { background: var(--brand-50); border-color: var(--brand-200); }
.doc-row-body { display: flex; flex-direction: column; gap: 6px; }
.doc-row-name { font-size: 13px; font-weight: 500; color: var(--fg); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.doc-row-meta { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.dot-sep { color: var(--fg-4); font-size: 10px; }
.count-pill { display: inline-flex; align-items: center; justify-content: center; min-width: 18px; height: 18px; padding: 0 5px; background: var(--bg-2); color: var(--fg-3); font-size: 10.5px; font-weight: 600; border-radius: 999px; border: 1px solid var(--line-2); }
.page-title { color: #fff !important; font-size: 15px; margin: 0; }
.page-sub { color: rgba(255,255,255,.82) !important; font-size: 11.5px; margin-top: 1px; }
.status { background: rgba(255,255,255,.18) !important; border-color: rgba(255,255,255,.3) !important; color: #fff !important; backdrop-filter: blur(8px); padding: 4px 10px !important; font-size: 11px !important; }
.status-dot { background: #fff !important; box-shadow: 0 0 0 3px rgba(255,255,255,.25), 0 0 12px rgba(255,255,255,.6) !important; }
.qa-title-row { display: flex; align-items: center; gap: 10px; }
.qa-title { margin: 0; font-size: 22px; font-weight: 600; letter-spacing: -.015em; background: linear-gradient(180deg, var(--fg) 30%, var(--accent-2) 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.qa-pill { display: inline-flex; align-items: center; flex-shrink: 0; font-size: 11px; color: #fff; background: var(--grad-2); border: 0; padding: 3px 9px; border-radius: 6px; font-family: "JetBrains Mono",ui-monospace,Menlo,Consolas,monospace; font-weight: 600; box-shadow: 0 4px 10px rgba(99,102,241,.28); }
.tag { display: inline-flex; align-items: center; font-size: 11px; font-weight: 500; padding: 2px 7px; border-radius: 4px; letter-spacing: .01em; }
.tag-fw { background: linear-gradient(135deg, #F3F0FF, #EDE9FE); color: var(--accent-2); border: 1px solid var(--brand-200); font-weight: 600; }
.src-score { margin-left: auto; font-size: 11px; color: #fff; background: var(--grad-2); padding: 2px 7px; border-radius: 4px; font-variant-numeric: tabular-nums; font-weight: 600; box-shadow: 0 2px 6px rgba(99,102,241,.28); }
.ragas-high::before { background: linear-gradient(180deg, #34D399, #10B981, #059669); }
.ragas-mid::before  { background: linear-gradient(180deg, #FBBF24, #F59E0B, #D97706); }
.ragas-low::before  { background: linear-gradient(180deg, #FB7185, #F43F5E, #E11D48); }
.ragas-high .ragas-fill { background: linear-gradient(90deg, #34D399, #10B981, #059669); box-shadow: 0 0 12px rgba(16,185,129,.45); }
.ragas-high .ragas-value { color: #047857; }
.ragas-mid .ragas-fill { background: linear-gradient(90deg, #FBBF24, #F59E0B, #D97706); box-shadow: 0 0 12px rgba(245,158,11,.45); }
.ragas-mid .ragas-value { color: #B45309; }
.ragas-low .ragas-fill { background: linear-gradient(90deg, #FB7185, #F43F5E, #E11D48); box-shadow: 0 0 12px rgba(244,63,94,.45); }
.ragas-low .ragas-value { color: #BE123C; }
.ragas-overall { font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 4px; font-variant-numeric: tabular-nums; }
.ragas-overall.ragas-high { background: var(--green-50); color: #047857; border: 1px solid #A7F3D0; }
.ragas-overall.ragas-mid  { background: var(--amber-50); color: #B45309; border: 1px solid #FDE68A; }
@keyframes pulse-dot { 0%, 100% { box-shadow: 0 0 0 3px var(--brand-100), 0 0 8px var(--brand-300); } 50% { box-shadow: 0 0 0 4px var(--brand-100), 0 0 16px var(--brand-3); } }
"""

# Streamlitコンポーネントへのデザイントークンマッピング
streamlit_overrides = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
html, body, [class*="css"], .stApp {
  font-family: "Inter","Noto Sans SC",-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif !important;
}
[data-testid="stApp"], .stApp { background: var(--bg) !important; }

/* Language Switcher Popover Injection */
div[data-testid="stPopover"] {
  position: fixed !important;
  top: 16px !important;
  right: 32px !important;
  left: auto !important;
  width: auto !important;
  z-index: 1001 !important;
}
div[data-testid="stPopover"] button {
  display: inline-flex !important; align-items: center !important; gap: 6px !important;
  height: 28px !important; padding: 0 8px 0 9px !important;
  background: rgba(255,255,255,.18) !important;
  border: 1px solid rgba(255,255,255,.3) !important;
  border-radius: 999px !important;
  color: #fff !important;
  font-size: 11.5px !important; font-weight: 500 !important;
  backdrop-filter: blur(8px) !important;
  min-height: 28px !important;
  box-shadow: none !important;
  transition: background .15s, border-color .15s;
}
div[data-testid="stPopover"] button:hover {
  background: rgba(255,255,255,.28) !important;
  border-color: rgba(255,255,255,.45) !important;
}
div[data-testid="stPopover"] button p {
  font-size: 11.5px !important; font-weight: 500 !important; margin: 0 !important;
  font-variant-numeric: tabular-nums; letter-spacing: .02em; min-width: 14px; text-align: center;
}
div[data-testid="stPopoverBody"] {
  min-width: 172px !important;
  max-width: 210px !important;
  background: #fff !important;
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
  box-shadow: 0 16px 40px rgba(15,15,26,.18), 0 2px 6px rgba(15,15,26,.08) !important;
  padding: 0 !important;
  overflow: hidden !important;
}
/* reset inner vertical gap */
div[data-testid="stPopoverBody"] [data-testid="stVerticalBlock"] {
  gap: 2px !important; padding: 4px !important;
}
/* section header injected via st.markdown */
.lang-hdr {
  font-size: 12.5px !important; font-weight: 600; letter-spacing: .06em;
  text-transform: uppercase; color: var(--fg-4);
  white-space: nowrap;
  padding: 8px 12px 6px; margin: 0;
  border-bottom: 1px solid var(--line);
}
div[data-testid="stPopoverBody"] [data-testid="stMarkdownContainer"]:has(.lang-hdr) {
  margin: 0 -4px !important; padding: 0 !important;
}
div[data-testid="stPopoverBody"] button {
  display: flex !important; align-items: center !important; gap: 8px !important;
  width: 100% !important; padding: 7px 10px !important;
  background: transparent !important; border: 0 !important; border-radius: 6px !important;
  color: var(--fg) !important; font-size: 12.5px !important; justify-content: flex-start !important;
  min-height: 0 !important; height: auto !important;
  text-align: left !important;
}
div[data-testid="stPopoverBody"] button:hover { background: var(--bg-2) !important; color: var(--fg) !important; border-color: transparent !important; }
/* selected lang — primary button type */
div[data-testid="stPopoverBody"] [data-testid="baseButton-primary"],
div[data-testid="stPopoverBody"] button[kind="primary"] {
  background: var(--brand-50) !important;
  color: var(--accent) !important;
  font-weight: 600 !important;
}
div[data-testid="stPopoverBody"] [data-testid="baseButton-primary"]:hover,
div[data-testid="stPopoverBody"] button[kind="primary"]:hover {
  background: var(--brand-100) !important;
}
div[data-testid="stPopoverBody"] button p { margin: 0 !important; width: 100%; font-size: 12.5px !important; }

/* Streamlitのトップメニュー・フッターを非表示 */
#MainMenu, footer { visibility: hidden; height: 0; }
header[data-testid="stHeader"] { height: 0 !important; min-height: 0 !important; background: transparent !important; box-shadow: none !important; overflow: visible !important; }
.stAppDeployButton { display: none !important; }

/* サイドバー展開ボタンのz-indexを上げてTopbarに隠れないようにする */
[data-testid="stSidebarExpandButton"], 
[data-testid="stSidebarCollapseButton"] {
  z-index: 9999999 !important;
  color: #0F0F1A !important;
  background-color: rgba(255, 255, 255, 0.8) !important;
  border-radius: 50% !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.2) !important;
  margin-top: 8px !important;
  margin-left: 8px !important;
}
[data-testid="stSidebarExpandButton"]:hover, 
[data-testid="stSidebarCollapseButton"]:hover {
  background-color: white !important;
}
/* 提升外层包裹器层级 */
[data-testid="stSidebarCollapsedControl"] {
  z-index: 9999998 !important;
}

/* メインエリアのマージンとパディング */
.block-container { 
  padding-top: 64px !important; 
  padding-bottom: 120px !important; 
  padding-left: 32px !important; 
  padding-right: 32px !important; 
  max-width: 100% !important;
  margin: 0 !important;
}

/* ================= サイドバー ================= */
section[data-testid="stSidebar"][aria-expanded="true"] {
  background: var(--sidebar-bg) !important;
  border-right: 1px solid var(--line);
  width: 300px !important;
  min-width: 300px !important;
}
.brand {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 300px !important;
  height: 60px !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 0 1.5rem !important;
  border-bottom: 1px solid var(--line) !important;
  background: var(--sidebar-bg) !important;
  box-sizing: border-box !important;
  z-index: 1000 !important;
  margin: 0 !important;
}

section[data-testid="stSidebar"] div[data-testid="stHorizontalBlock"] {
  align-items: center !important;
}
section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] p {
  margin-bottom: 0 !important;
}

section[data-testid="stSidebar"] .stButton {
  display: flex;
  justify-content: flex-end;
}
section[data-testid="stSidebar"] button[kind="secondary"],
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
  width: 34px !important;
  height: 34px !important;
  min-height: 34px !important;
  padding: 0 !important;
  background: transparent !important;
  border: 1px solid var(--line-2) !important;
  border-radius: 6px !important;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--fg-4) !important;
}
section[data-testid="stSidebar"] button[kind="secondary"]:hover,
section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
  background: var(--rose-50) !important;
  color: var(--rose) !important;
  border-color: #FECDD3 !important;
}

section[data-testid="stSidebar"] [data-baseweb="input"] > div,
section[data-testid="stSidebar"] [data-baseweb="textarea"] > div,
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: var(--r-sm) !important;
  font-size: 13px !important;
  color: var(--fg) !important;
  box-shadow: none !important;
  min-height: 34px !important;
}
section[data-testid="stSidebar"] [data-baseweb="input"] > div:focus-within,
section[data-testid="stSidebar"] [data-baseweb="textarea"] > div:focus-within,
section[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {
  border-color: var(--brand-3) !important;
  box-shadow: 0 0 0 3px var(--brand-50) !important;
}
/* 内部input（selectのcomboboxなど）のボーダーを無効化 */
[data-baseweb="select"] input {
  border: none !important;
  box-shadow: none !important;
  background: transparent !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] label,
section[data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
  font-size: 11px !important; color: var(--fg-4) !important; font-weight: 600 !important;
  margin-bottom: 4px !important; letter-spacing: .08em !important; text-transform: uppercase !important;
}

section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
  background: var(--bg-2) !important;
  border: 1px dashed var(--line-3) !important;
  border-radius: var(--r-md) !important;
  padding: 24px 12px !important;
  transition: background .15s, border-color .15s;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section:hover {
  background: var(--brand-50) !important;
  border-color: var(--brand-200) !important;
}

/* デフォルトのアップロードプロンプトテキストとアイコンのみ非表示、他は保持 */
[data-testid="stFileUploaderDropzone"] [data-testid="stMarkdownContainer"],
[data-testid="stFileUploaderDropzone"] button[kind="secondary"] {
  display: none !important;
}
/* ドロップゾーンをクリック可能にする */
[data-testid="stFileUploaderDropzone"] {
  position: relative !important;
  cursor: pointer !important;
  min-height: 120px !important;
}
[data-testid="stFileUploaderDropzone"]::before {
  /* コンテンツは動的に挿入 */
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--fg);
  margin-top: 8px;
  margin-bottom: 4px;
  text-align: center;
  padding-top: 48px;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='40' height='42' fill='none' viewBox='0 0 40 42'%3E%3Crect width='36' height='36' x='2' y='4' fill='%23000000' fill-opacity='0.05' rx='10'/%3E%3Crect width='36' height='36' x='2' y='2' fill='%23ffffff' rx='10' stroke='%23E5E7EB' stroke-width='1'/%3E%3Cpath stroke='%234B5563' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.8' d='M20 22V12m0 0l-4 4m4-4l4 4M14 25v1.5a1.5 1.5 0 0 0 1.5 1.5h9a1.5 1.5 0 0 0 1.5-1.5V25'/%3E%3C/svg%3E");
  background-position: center top;
  background-repeat: no-repeat;
}
[data-testid="stFileUploaderDropzone"]::after {
  /* コンテンツは動的に挿入 */
  display: block;
  font-size: 11px;
  color: var(--fg-4);
  text-align: center;
}

section[data-testid="stSidebar"] .stButton > button[kind="primary"] {
  width: 100%;
  background: var(--grad-1) !important;
  background-size: 150% 150% !important;
  color: #fff !important;
  border: 0 !important;
  border-radius: var(--r-sm) !important;
  height: 36px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  box-shadow: 0 6px 16px rgba(124,58,237,.28), inset 0 1px 0 rgba(255,255,255,.18) !important;
  transition: background-position .3s, transform .05s, box-shadow .2s !important;
}
section[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover {
  background-position: 100% 0 !important;
  box-shadow: 0 10px 22px rgba(124,58,237,.35) !important;
}

/* ================= メインエリア上部バナー（幅の完全修正） ================= */
.topbar-wrapper .topbar {
  position: fixed !important;
  top: 0 !important;
  left: 300px !important; /* サイドバー幅を300pxと想定 */
  right: 0 !important;
  height: 60px !important;
  padding: 0 32px !important;
  z-index: 1000 !important;
  background: var(--grad-aurora) !important;
  display: flex !important;
  justify-content: space-between !important;
  align-items: center !important;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
}
/* サイドバーが閉じている場合、topbarを全幅に */
@media (max-width: 768px) {
  .topbar-wrapper .topbar { left: 0 !important; }
}
[data-testid="stSidebar"][aria-expanded="false"] ~ div .topbar-wrapper .topbar {
  left: 0 !important;
}
[data-testid="stSidebar"][aria-expanded="false"] .brand {
  transform: translateX(-300px) !important;
  opacity: 0 !important;
}

.qa-head { padding-left: 0 !important; padding-right: 0 !important; margin-top: 10px !important; }
.qa-title { color: var(--fg-2) !important; -webkit-text-fill-color: var(--fg-2) !important; font-size: 26px !important; font-weight: 700 !important; }
.topbar-left { display: flex; flex-direction: column; }
.page-title { font-size: 15px !important; font-weight: 600 !important; color: white !important; margin-bottom: 2px !important; }
.page-sub { font-size: 11px !important; color: rgba(255,255,255,0.8) !important; }
.topbar-right { display: flex; align-items: center; padding-right: 84px !important; }
.status { display: inline-flex !important; align-items: center !important; gap: 6px !important; padding: 4px 12px !important; border: 1px solid rgba(255,255,255,.3) !important; border-radius: 999px !important; color: white !important; font-size: 11px !important; }
.status-dot { width: 6px !important; height: 6px !important; border-radius: 50% !important; background: white !important; flex-shrink: 0 !important; }

/* ================= メインエリアフォーム（フィルター） ================= */
.block-container [data-baseweb="input"] > div,
.block-container [data-baseweb="textarea"] > div,
.block-container [data-baseweb="select"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: var(--r-md) !important;
  font-size: 13px !important;
  min-height: 36px !important;
  box-shadow: none !important;
}
.block-container [data-baseweb="input"] > div:focus-within,
.block-container [data-baseweb="textarea"] > div:focus-within,
.block-container [data-baseweb="select"] > div:focus-within {
  border-color: var(--brand-3) !important;
  box-shadow: 0 0 0 3px var(--brand-50) !important;
}
.block-container label { font-size: 11px !important; font-weight: 600 !important;
  color: var(--fg-3) !important; letter-spacing: .04em; text-transform: uppercase; }

/* ================= チャットバブル（ピクセル単位の調整） ================= */
.msg-hook { display: none !important; }

[data-testid="stChatMessage"] {
  background: transparent !important;
  padding: 0 !important;
  margin-bottom: 24px !important;
  display: flex !important;
  width: 100% !important;
  gap: 16px !important;
  align-items: flex-start !important;
}

/* ユーザーメッセージ */
[data-testid="stChatMessage"]:has(.msg-user) {
  flex-direction: row-reverse !important;
  justify-content: flex-start !important;
  align-items: center !important;
}
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] {
  background: linear-gradient(135deg, #4F46E5, #7C3AED, #A855F7) !important;
  color: #fff !important;
  border-radius: 14px !important;
  border-top-right-radius: 4px !important;
  padding: 14px 18px !important;
  max-width: 75% !important;
  width: fit-content !important;
  flex: none !important;
  box-shadow: 0 10px 28px rgba(124,58,237,.32) !important;
  border: none !important;
  margin-left: auto !important;
  margin-right: 0 !important;
  align-self: center !important;
}
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] p { color: #fff !important; margin: 0 !important;}
/* 内部コンテナのスペーシングをゼロにしてテキストをバブル内にぴったり配置 */
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] [data-testid="stVerticalBlock"] {
  gap: 0 !important;
  padding: 0 !important;
  margin: 0 !important;
}
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] [data-testid="stMarkdownContainer"],
[data-testid="stChatMessage"]:has(.msg-user) [data-testid="stChatMessageContent"] .stMarkdown {
  margin: 0 !important;
  padding: 0 !important;
}

/* アシスタントメッセージ */
[data-testid="stChatMessage"]:has(.msg-assistant) {
  justify-content: flex-start !important;
}
[data-testid="stChatMessage"]:has(.msg-assistant) [data-testid="stChatMessageContent"] {
  background: #FFFFFF !important;
  border: 1px solid #E8E8F0 !important;
  border-radius: 14px !important;
  border-top-left-radius: 4px !important;
  padding: 16px 20px !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.04) !important;
  position: relative !important;
  overflow: visible !important;
  flex: 1 !important;
}
[data-testid="stChatMessage"]:has(.msg-assistant) [data-testid="stChatMessageContent"]::before {
  content: "" !important;
  position: absolute !important;
  left: -1px !important; top: -1px !important; bottom: -1px !important; width: 4px !important;
  background: linear-gradient(180deg, #4F46E5, #7C3AED, #A855F7) !important;
  border-radius: 14px 0 0 4px !important;
}

/* アバター */
[data-testid="stChatMessage"] > div:first-child {
  width: 36px !important; height: 36px !important; min-width: 36px !important;
  display: flex !important; align-items: center !important; justify-content: center !important;
  color: transparent !important;
  border-radius: 10px !important;
  overflow: hidden !important;
}
[data-testid="stChatMessage"] > div:first-child * { 
  display: none !important; 
}

[data-testid="stChatMessage"]:has(.msg-user) > div:first-child {
  align-self: center !important;
  margin-top: auto !important;
  margin-bottom: auto !important;
  background-color: #F3F4F6 !important;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%234B5563'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z'/%3E%3C/svg%3E") !important;
  background-size: 20px !important; background-position: center !important; background-repeat: no-repeat !important;
  border: 1px solid #E5E7EB !important;
}

[data-testid="stChatMessage"]:has(.msg-assistant) > div:first-child {
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z'/%3E%3C/svg%3E") center / 20px no-repeat, linear-gradient(135deg, #8B5CF6, #7C3AED) !important;
  border: none !important;
  box-shadow: 0 4px 14px rgba(139, 92, 246, 0.4) !important;
}
[data-testid="stExpander"] details {
  border: 1px solid var(--line) !important;
  border-radius: 10px !important;
  background: var(--bg) !important;
  margin-top: 10px !important;
}
[data-testid="stExpander"] summary { padding: 12px 14px !important; }
[data-testid="stExpander"] summary p { font-size: 13px !important; font-weight: 600 !important; color: var(--fg-3) !important; margin: 0 !important; }
[data-testid="stExpander"] summary:hover { background: var(--bg-2) !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] { padding: 16px !important; border-top: 1px solid var(--line); background: transparent !important; }

/* ================= チャット入力 ================= */
[data-testid="stChatInput"] {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: 16px !important;
  box-shadow: 0 12px 32px rgba(124,58,237,.08), 0 0 0 1px rgba(124,58,237,.04) !important;
  padding: 6px 8px !important;
}
[data-testid="stChatInput"] textarea { font-size: 14px !important; color: var(--fg) !important; }
[data-testid="stChatInputSubmitButton"] {
  background: linear-gradient(135deg, #4F46E5, #7C3AED) !important; color: white !important;
  border-radius: 10px !important; border: none !important;
}
[data-testid="stChatInputSubmitButton"] svg { fill: white !important; }

/* ソースカードのスタイル崩れを防止 */
.src-grid { display: grid !important; grid-template-columns: 1fr 1fr !important; gap: 12px !important; }
.src-card { background: white !important; padding: 14px !important; border: 1px solid var(--line) !important; border-radius: 10px !important; }
.ragas-grid { display: grid !important; grid-template-columns: 1fr 1fr 1fr !important; gap: 12px !important; }
"""

dynamic_css = f"""
  [data-testid="stFileUploaderDropzone"]::before {{
    content: "{t['drop_text']}";
  }}
  [data-testid="stFileUploaderDropzone"]::after {{
    content: "{t['drop_meta']}";
  }}
"""
st.markdown(f"<style>\n{styles_css}\n{streamlit_overrides}\n{dynamic_css}\n</style>", unsafe_allow_html=True)

# --- ヘルパー関数 ---
def get_docs_count():
    try:
        results, _ = client.scroll(
            collection_name=COLLECTION_NAME,
            with_payload=True,
            limit=1000,
        )
        filenames = {r.payload["filename"]: r.payload for r in results if "filename" in r.payload}
        return len(filenames), filenames
    except Exception:
        return 0, {}

docs_count, docs_dict = get_docs_count()

# ── サイドバー：ドキュメント管理 ──────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="brand">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="#7C3AED" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0;">
          <rect x="3" y="3" width="8" height="8" rx="2" fill-opacity="0.6"/>
          <rect x="13" y="3" width="8" height="8" rx="2"/>
          <rect x="3" y="13" width="8" height="8" rx="2"/>
          <rect x="13" y="13" width="8" height="8" rx="2"/>
        </svg>
        <div class="brand-text">
            <span class="brand-title">{t['sidebar_kb']}</span>
            <span class="brand-sub">{t['sidebar_kb_en']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="side-label">{t["upload"]}</div>', unsafe_allow_html=True)
    
    uploaded_files = st.file_uploader(
        t["drop_text"],
        type=["pdf", "md"],
        accept_multiple_files=True,
        label_visibility="collapsed"
    )
    st.markdown(f'<div class="side-label">{t["fw_name"]}</div>', unsafe_allow_html=True)
    framework = st.text_input(t["fw_name"], placeholder=t["fw_name_ph"], label_visibility="collapsed")
    st.markdown(f'<div class="side-label">{t["doc_type"]}</div>', unsafe_allow_html=True)
    doc_type = st.selectbox(t["doc_type"], [t["type_tutorial"], t["type_api"], "changelog", t["type_other"]], label_visibility="collapsed")

    if st.button(t["add_btn"], type="primary", use_container_width=True):
        if not uploaded_files:
            st.warning("请先选择文件")
        elif not framework:
            st.warning("请输入框架名称")
        else:
            for f in uploaded_files:
                with st.spinner(f"正在处理 {f.name}..."):
                    count = upload_document(f, framework, doc_type)
                    st.success(f"{f.name} 上传完成")
            st.rerun()

    st.markdown('<div class="side-divider"></div>', unsafe_allow_html=True)
    
    st.markdown(f'<div class="side-label">{t["uploaded"]} <span class="count-pill">{docs_count}</span></div>', unsafe_allow_html=True)
    
    if not docs_dict:
        st.info(t["empty_kb"])
    else:
        # ドキュメント種別の翻訳マップ
        doc_type_map = {
            "教程": t["type_tutorial"],
            "API文档": t["type_api"],
            "changelog": "changelog",
            "其他": t["type_other"],
            # English
            "Tutorial": t["type_tutorial"],
            "API Docs": t["type_api"],
            "Other": t["type_other"],
            # Japanese
            "ﾁｭｰﾄﾘｱﾙ": t["type_tutorial"],
            "API ﾄﾞｷｭﾒﾝﾄ": t["type_api"],
        }
        
        for fname, payload in docs_dict.items():
            fw = payload.get("framework", "")
            dt_raw = payload.get("doc_type", "")
            dt = doc_type_map.get(dt_raw, dt_raw)  # Translate or use original
            
            c1, c2 = st.columns([0.8, 0.2], gap="small", vertical_alignment="center")
            with c1:
                st.markdown(f"""
                <div class="doc-row">
                  <div class="doc-row-body">
                    <div class="doc-row-name" title="{fname}">{fname}</div>
                    <div class="doc-row-meta">
                      <span class="tag tag-fw">{fw}</span>
                      <span class="dot-sep">·</span>
                      <span class="tag tag-fw">{dt}</span>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                if st.button("🗑", key=f"del_{fname}", help="删除"):
                    try:
                        with st.spinner(f"删除中..."):
                            client.delete(
                                collection_name=COLLECTION_NAME,
                                points_selector=FilterSelector(
                                    filter=Filter(
                                        must=[FieldCondition(key="filename", match=MatchValue(value=fname))]
                                    )
                                )
                            )
                            st.rerun()
                    except Exception as e:
                        st.error(f"删除失败: {e}")

    # フッターステータス
    if st.session_state.index_status == "ready":
        st.markdown(f"""
        <div class="side-foot">
          <span style="color: var(--green); font-size: 16px; line-height: 1;">✅</span>
          {t['ready']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="side-foot" style="color: var(--rose);">
          <span style="font-size: 16px; line-height: 1;">❌</span>
          {t['error']}
        </div>
        """, unsafe_allow_html=True)
        if st.button(t['retry'], key="retry_connection", use_container_width=True):
            try:
                ensure_collection()
                st.session_state.index_status = "ready"
                st.session_state.error_msg = None
                st.rerun()
            except Exception as e:
                st.session_state.error_msg = str(e)
                st.error(f"连接失败: {e}")
        if st.session_state.error_msg:
            st.caption(f"⚠️ {st.session_state.error_msg}")
    
    # 作者情報
    st.markdown("""
    <div class="side-author">
      Built by <a href="https://github.com/aeolusyansheng19810626" target="_blank">Sheng Yan</a> · <a href="https://github.com/aeolusyansheng19810626/qdrant-knowledge-base" target="_blank">GitHub</a>
    </div>
    """, unsafe_allow_html=True)

# ── メインエリア：質問応答 ──────────────────────────────────────────
st.markdown(f"""
<div class="topbar-wrapper">
<div class="topbar">
  <div class="topbar-left">
    <div class="page-title">{t['title']}</div>
    <div class="page-sub">{t['subtitle']}</div>
  </div>
  <div class="topbar-right">
    <div class="status">
      <span class="status-dot"></span>
      <span>{t['docs_count'].format(docs_count)}</span>
    </div>
  </div>
</div>
</div>
<div class="qa-head">
  <div class="qa-title-row">
    <div class="qa-title">{t['qa_title']}</div>
    <div class="qa-pill">/ {t['ask']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# 言語切り替えポップオーバー
pop_col = st.container()
with pop_col:
    lang_labels = {"zh": "中", "en": "EN", "ja": "日"}
    cur_label = lang_labels[st.session_state.lang]
    with st.popover(f"🌐 {cur_label}"):
        st.markdown('<p class="lang-hdr">LANGUAGE / 语言</p>', unsafe_allow_html=True)
        for code, abbr, name in [("zh", "CN", "简体中文"), ("ja", "JP", "日本語"), ("en", "EN", "English")]:
            active = st.session_state.lang == code
            label = f"{abbr}  {name}  ✓" if active else f"{abbr}  {name}"
            if st.button(label, use_container_width=True,
                         type="primary" if active else "secondary",
                         key=f"lang_{code}"):
                st.session_state.lang = code
                st.rerun()

# フィルター
col1, col2 = st.columns(2, gap="medium")
with col1:
    filter_framework = st.text_input(t["framework"], placeholder=t["framework_ph"])
with col2:
    filter_doc_type = st.selectbox(t["doc_type"], [t["type_all"], t["type_tutorial"], t["type_api"], "changelog", t["type_other"]])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- レンダリングヘルパー ---
def tier(v): 
    return "high" if v >= 0.8 else "mid" if v >= 0.6 else "low"

def ragas_row(label, v):
    pct = int(v * 100)
    t = tier(v)
    return f"""<div class="ragas-row ragas-{t}">
<div class="ragas-head">
<span class="ragas-label">{label}</span>
<span class="ragas-value">{pct}<span class="ragas-pct">%</span></span>
</div>
<div class="ragas-track"><div class="ragas-fill" style="width:{pct}%"></div></div>
</div>"""

def render_sources(sources):
    if not sources: return
    with st.expander(f"{t['src_docs']}  {len(sources)}", expanded=True):
        cards = "".join([f"""<div class="src-card">
<div class="src-head">
<span class="tag tag-fw">{s['framework']}</span>
<span class="src-type">{s['doc_type']}</span>
<span class="src-score">{t['related'].format(int(s['score']*100))}</span>
</div>
<div class="src-title">{s['filename']}</div>
<div class="src-quote">{s['text']}</div>
<div class="src-foot">📄 {s['filename']} <span class="src-loc">{t['paragraph'].format(s['chunk_index'])}</span></div>
</div>""" for s in sources])
        st.markdown(f'<div class="src-grid">{cards}</div>', unsafe_allow_html=True)

def render_ragas(ragas):
    with st.expander(f"📊 {t['eval_scores']}", expanded=True):
        if not ragas:
            err_msg = {
                "zh": "⚠️ 评估暂时不可用（API 限速或网络超时）",
                "en": "⚠️ Evaluation temporarily unavailable (API rate limit or network timeout)",
                "ja": "⚠️ 評価は一時的に利用できません（API制限またはネットワークタイムアウト）"
            }
            st.caption(err_msg.get(st.session_state.lang, "⚠️ 评估暂时不可用（API 限速或网络超时）"))
            return
        st.markdown(f"""<div class="ragas-grid">
{ragas_row(t["faithfulness"],  ragas.get('faithfulness', 0))}
{ragas_row(t["relevancy"], ragas.get('answer_relevancy', 0))}
{ragas_row(t["precision"], ragas.get('context_precision', 0))}
</div>""", unsafe_allow_html=True)

# チャット履歴の表示
for msg in st.session_state.chat_history:
    avatar_arg = "✨" if msg["role"] == "assistant" else None
    with st.chat_message(msg["role"], avatar=avatar_arg):
        if msg["role"] == "user":
            st.markdown(f'<span class="msg-hook msg-user"></span>{msg["content"]}', unsafe_allow_html=True)
        else:
            st.markdown('<span class="msg-hook msg-assistant"></span>', unsafe_allow_html=True)
            st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if msg.get("sources"):
                render_sources(msg["sources"])
            if msg.get("eval_scores"):
                render_ragas(msg["eval_scores"])

# 入力欄
if query := st.chat_input(t["chat_ph"]):
    with st.chat_message("user"):
        st.markdown(f'<span class="msg-hook msg-user"></span>{query}', unsafe_allow_html=True)
    st.session_state.chat_history.append({"role": "user", "content": query})

    with st.chat_message("assistant", avatar="✨"):
        st.markdown('<span class="msg-hook msg-assistant"></span>', unsafe_allow_html=True)
        with st.spinner(t["searching"]):
            dt_filter = filter_doc_type if filter_doc_type != "全部" else None
            answer, sources = search(
                query,
                framework=filter_framework if filter_framework else None,
                doc_type=dt_filter,
                lang=st.session_state.lang,
            )
        st.markdown(answer)
        
        if sources:
            render_sources(sources)

        # バックグラウンド評価
        eval_scores = None
        contexts = [s["text_full"] for s in sources] if sources else []
        if contexts:
            spinner_msg = {
                "zh": "📊 RAGAS 评估中...",
                "en": "📊 Running RAGAS Evaluation...",
                "ja": "📊 RAGAS 評価中..."
            }
            with st.spinner(spinner_msg.get(st.session_state.lang, "📊 RAGAS 评估中...")):
                eval_scores = run_evaluation(query, answer, contexts)
        render_ragas(eval_scores)

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "eval_scores": eval_scores,
    })
