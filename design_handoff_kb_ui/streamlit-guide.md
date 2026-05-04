# AI 技术文档知识库 · Streamlit UI 重设计

> 风格：Notion / Linear · 浅色高级灰 + 靛蓝主色 · Inter + Noto Sans SC

---

## 1. 整体布局结构建议

```
┌──────────────────────────────────────────────────────────────────┐
│  st.sidebar (296px, 白底, 右侧 1px 分隔)                          │
│  ┌──────────────────────────┐                                    │
│  │ 🟦 知识库 / Knowledge Base │   <-- brand                       │
│  ├──────────────────────────┤                                    │
│  │ 上传文档                   │   <-- 11px 大写小标题              │
│  │ ┌─ Drop Zone ─────────┐  │                                    │
│  │ │  ⬆  拖拽或点击上传    │  │   st.file_uploader (CSS 改造)     │
│  │ │  PDF · MD · ≤200MB   │  │                                    │
│  │ └─────────────────────┘  │                                    │
│  │ 框架名称 [____________]   │   st.text_input                    │
│  │ 文档类型 [教程       ▾]   │   st.selectbox                     │
│  │ [ + 添加到知识库       ]   │   st.button (primary)             │
│  ├──────────────────────────┤                                    │
│  │ 已上传文档        ④       │                                    │
│  │ 📄 LangChain-Cookbook…  🗑 │   自定义 row (st.markdown HTML)   │
│  │ 📄 LangGraph-API…       🗑 │                                    │
│  │ 📄 qdrant-vector…       🗑 │                                    │
│  ├──────────────────────────┤                                    │
│  │ ● 本地索引 · 已就绪       │   footer status                    │
│  └──────────────────────────┘                                    │
│                                                                  │
│  Main (32px 内边距)                                               │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │ AI 技术文档知识库              [● 向量库 · 12 文档]         │    │
│  │ 基于 RAG 的文档问答 · 检索增强生成                          │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │ 文档问答  /Ask                                             │    │
│  │ ┌─ 框架 ────────────────┐ ┌─ 文档类型 ─┐                   │    │
│  │ │ 🔍 留空则搜索全部       │ │ 全部     ▾│                   │    │
│  │ └────────────────────────┘ └───────────┘                   │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │                                                          │    │
│  │              [user bubble (靛蓝, 右对齐)]   👤            │    │
│  │                                                          │    │
│  │  ✨ ┌──────────────────────────────────────────────┐      │    │
│  │     │ AI 回答正文…                                  │      │    │
│  │     │ ┌─ ▾ 来源文档  ③ ────────────────────────┐  │      │    │
│  │     │ │ [LangChain] 教程   相关度 92%           │  │      │    │
│  │     │ │ 标题 / 引用 / 文件 · 第 3 段             │  │      │    │
│  │     │ └────────────────────────────────────────┘  │      │    │
│  │     │ ┌─ ▾ RAGAS 评估分数  综合 82 ─────────────┐  │      │    │
│  │     │ │ Faithfulness   91%  ████████████░       │  │      │    │
│  │     │ │ Relevancy      84%  ██████████░░ (绿)   │  │      │    │
│  │     │ │ Precision      72%  ████████░░░░ (黄)   │  │      │    │
│  │     │ └────────────────────────────────────────┘  │      │    │
│  │     └──────────────────────────────────────────────┘      │    │
│  ├──────────────────────────────────────────────────────────┤    │
│  │ ┌─ Composer ───────────────────────────────────────────┐ │    │
│  │ │ 用中文提问，例如：LangGraph 怎么定义节点？             │ │    │
│  │ │ ↵ 发送 · ⇧↵ 换行                              [ → ]  │ │    │
│  │ └──────────────────────────────────────────────────────┘ │    │
│  └──────────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────┘
```

**关键 Streamlit 组件映射：**

| 区域 | 推荐组件 |
|---|---|
| 上传区 | `st.sidebar` + `st.file_uploader`（accept_multiple_files=True） |
| 框架/类型 | `st.text_input` + `st.selectbox` |
| 上传按钮 | `st.button("添加到知识库", type="primary")` |
| 已上传列表 | 用 `st.container` + `st.columns([1, 6, 1])` 自定义每行；删除按钮用带 key 的 `st.button` |
| 标题区 | `st.markdown` 注入自定义 HTML（含状态徽章） |
| 过滤器 | `st.columns(2)` → text_input + selectbox |
| 对话区 | `st.chat_message("user" / "assistant")` + 自定义 CSS 改造气泡 |
| 来源 / RAGAS | `st.expander("来源文档") / st.expander("RAGAS 评估分数")` + 自定义 HTML |
| 输入框 | `st.chat_input("用中文提问…")` |

---

## 2. Streamlit 注入式 CSS（直接 `st.markdown(CSS, unsafe_allow_html=True)`）

```python
import streamlit as st

st.set_page_config(page_title="AI 技术文档知识库", layout="wide", initial_sidebar_state="expanded")

CSS = r"""
<style>
/* ================= Fonts ================= */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  --bg:#FAFAFA; --bg-2:#F4F4F5; --surface:#FFFFFF;
  --line:#ECECEE; --line-2:#E4E4E7; --line-3:#D4D4D8;
  --fg:#18181B; --fg-2:#3F3F46; --fg-3:#71717A; --fg-4:#A1A1AA;
  --brand:#4F46E5; --brand-2:#6366F1; --brand-3:#818CF8;
  --brand-50:#EEF2FF; --brand-100:#E0E7FF; --brand-200:#C7D2FE;
  --green:#10B981; --green-50:#ECFDF5;
  --amber:#F59E0B; --amber-50:#FFFBEB;
  --rose:#F43F5E;  --rose-50:#FFF1F2;
  --r-sm:6px; --r-md:10px; --r-lg:14px;
  --shadow-sm: 0 1px 2px rgba(24,24,27,.04), 0 0 0 1px rgba(24,24,27,.04);
  --shadow-md: 0 4px 16px rgba(24,24,27,.06), 0 0 0 1px rgba(24,24,27,.05);
}

html, body, [class*="css"], .stApp {
  font-family: "Inter","Noto Sans SC",-apple-system,BlinkMacSystemFont,
               "Segoe UI","PingFang SC","Microsoft YaHei",sans-serif !important;
  color: var(--fg);
  -webkit-font-smoothing: antialiased;
}
.stApp { background: var(--bg); }

/* 隐藏 Streamlit 顶部菜单/页脚 */
#MainMenu, footer, header[data-testid="stHeader"] { visibility: hidden; height: 0; }
.block-container { padding-top: 1.25rem !important; padding-bottom: 5rem !important; max-width: 980px; }

/* ================= Sidebar ================= */
section[data-testid="stSidebar"] {
  background: var(--surface) !important;
  border-right: 1px solid var(--line);
  width: 296px !important;
  min-width: 296px !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0.5rem; }

/* sidebar 小标题 (用 st.markdown('<div class="side-label">…</div>')) */
.side-label {
  font-size: 11px; font-weight: 600; letter-spacing: .08em;
  text-transform: uppercase; color: var(--fg-4);
  margin: 18px 4px 8px; display: flex; align-items: center; gap: 6px;
}
.side-divider { height:1px; background: var(--line); margin: 14px 0; }

/* sidebar 内输入框 */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: var(--r-sm) !important;
  font-size: 13px !important;
  color: var(--fg) !important;
  box-shadow: none !important;
  min-height: 34px !important;
}
section[data-testid="stSidebar"] input:focus,
section[data-testid="stSidebar"] textarea:focus {
  border-color: var(--brand-3) !important;
  box-shadow: 0 0 0 3px var(--brand-50) !important;
}
section[data-testid="stSidebar"] label {
  font-size: 12px !important; color: var(--fg-3) !important; font-weight: 500 !important;
  margin-bottom: 4px !important;
}

/* file_uploader → drop 区 */
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section {
  background: var(--bg-2) !important;
  border: 1px dashed var(--line-3) !important;
  border-radius: var(--r-md) !important;
  padding: 14px 12px !important;
  transition: background .15s, border-color .15s;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section:hover {
  background: var(--brand-50) !important;
  border-color: var(--brand-200) !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] button {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  color: var(--fg-2) !important;
  font-size: 12px !important;
  border-radius: 6px !important;
  height: 30px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] small { color: var(--fg-4) !important; font-size: 11px !important; }

/* sidebar 主按钮（"添加到知识库"） */
section[data-testid="stSidebar"] .stButton > button[kind="primary"],
section[data-testid="stSidebar"] .stButton > button {
  width: 100%;
  background: var(--fg) !important;
  color: #fff !important;
  border: 0 !important;
  border-radius: var(--r-sm) !important;
  height: 36px !important;
  font-weight: 500 !important;
  font-size: 13px !important;
  box-shadow: var(--shadow-sm) !important;
  transition: background .15s !important;
}
section[data-testid="stSidebar"] .stButton > button:hover { background: #000 !important; }

/* 已上传列表的每一行 (用 HTML 渲染) */
.doc-row {
  display: grid; grid-template-columns: 22px 1fr auto;
  align-items: center; gap: 8px;
  padding: 8px; border-radius: 6px;
}
.doc-row:hover { background: var(--bg-2); }
.doc-row .ico {
  width: 22px; height: 22px; border-radius: 5px;
  background: var(--bg-2); border: 1px solid var(--line);
  display: grid; place-items: center; color: var(--fg-3);
}
.doc-row .name { font-size: 12.5px; color: var(--fg); font-weight: 500;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.doc-row .meta { font-size: 11px; color: var(--fg-4); margin-top: 2px; display:flex; gap:6px; }
.doc-row .tag-fw {
  font-size: 11px; padding: 1px 6px; border-radius: 4px;
  background: var(--brand-50); color: var(--brand);
  border: 1px solid var(--brand-100);
}

/* sidebar footer */
.side-foot {
  margin-top: 12px; padding: 10px 4px;
  border-top: 1px solid var(--line);
  font-size: 11.5px; color: var(--fg-3);
  display: flex; align-items: center; gap: 8px;
}
.side-foot .dot { width:6px; height:6px; border-radius:50%;
  background: var(--green); box-shadow: 0 0 0 3px var(--green-50); }

/* ================= Main: 标题 ================= */
.kb-topbar {
  display: flex; align-items: center; justify-content: space-between;
  padding-bottom: 14px; margin-bottom: 14px;
  border-bottom: 1px solid var(--line);
}
.kb-title { font-size: 18px; font-weight: 600; letter-spacing: -.01em; margin:0; }
.kb-sub   { font-size: 12px; color: var(--fg-4); margin-top: 2px; }
.kb-status {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 5px 10px; font-size: 11.5px; color: var(--fg-3);
  background: var(--surface); border: 1px solid var(--line-2);
  border-radius: 999px;
}
.kb-status .dot { width:6px; height:6px; border-radius:50%;
  background: var(--brand); box-shadow: 0 0 0 3px var(--brand-50); }

.qa-title-row { display:flex; align-items:center; gap:10px; margin: 6px 0 12px; }
.qa-title { margin:0; font-size: 22px; font-weight: 600; letter-spacing: -.015em; }
.qa-pill {
  font-size: 11px; color: var(--brand);
  background: var(--brand-50); border: 1px solid var(--brand-100);
  padding: 3px 8px; border-radius: 6px;
  font-family: "JetBrains Mono", ui-monospace, monospace;
}

/* ================= 主区表单（过滤器） ================= */
.block-container [data-baseweb="input"] > div,
.block-container [data-baseweb="select"] > div,
.block-container input, .block-container textarea {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: var(--r-md) !important;
  font-size: 13px !important;
  min-height: 36px !important;
  box-shadow: none !important;
}
.block-container input:focus, .block-container textarea:focus {
  border-color: var(--brand-3) !important;
  box-shadow: 0 0 0 3px var(--brand-50) !important;
}
.block-container label { font-size: 11px !important; font-weight: 600 !important;
  color: var(--fg-3) !important; letter-spacing: .04em; text-transform: uppercase; }

/* ================= 对话气泡 ================= */
[data-testid="stChatMessage"] {
  background: transparent !important;
  padding: 0 !important;
  margin-bottom: 18px;
}
/* user 气泡 — 右对齐, 靛蓝 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
  flex-direction: row-reverse;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
  background: var(--brand) !important;
  color: #fff !important;
  border-radius: var(--r-lg) !important;
  border-bottom-right-radius: 4px !important;
  padding: 12px 16px !important;
  max-width: 70%;
  box-shadow: 0 6px 20px rgba(79,70,229,.18);
}
/* assistant 气泡 — 左对齐, 白底 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
  background: var(--surface) !important;
  border: 1px solid var(--line) !important;
  border-radius: var(--r-lg) !important;
  border-bottom-left-radius: 4px !important;
  padding: 14px 16px !important;
  box-shadow: var(--shadow-sm);
}
/* assistant 头像 — 靛蓝渐变 + sparkle */
[data-testid="chatAvatarIcon-assistant"] {
  background: linear-gradient(135deg, var(--brand) 0%, var(--brand-2) 100%) !important;
  color: #fff !important;
  border-radius: 8px !important;
  box-shadow: 0 4px 10px rgba(79,70,229,.25);
}
[data-testid="chatAvatarIcon-user"] {
  background: var(--bg-2) !important;
  color: var(--fg-2) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: 8px !important;
}

/* ================= Expander (来源 / RAGAS) ================= */
[data-testid="stExpander"] {
  border: 1px solid var(--line) !important;
  border-radius: var(--r-md) !important;
  background: var(--bg) !important;
  margin-top: 10px !important;
  overflow: hidden;
}
[data-testid="stExpander"] summary {
  padding: 10px 12px !important;
  font-size: 12.5px !important; font-weight: 600 !important;
  color: var(--fg-2) !important;
}
[data-testid="stExpander"] summary:hover { background: var(--bg-2) !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
  background: var(--surface) !important;
  border-top: 1px solid var(--line);
  padding: 12px !important;
}

/* ================= 来源卡片 (HTML 注入) ================= */
.src-grid { display:grid; grid-template-columns: 1fr 1fr; gap: 10px; }
@media (max-width: 760px){ .src-grid { grid-template-columns: 1fr; } }
.src-card {
  background: var(--bg); border: 1px solid var(--line);
  border-radius: var(--r-md); padding: 12px;
  display:flex; flex-direction:column; gap:8px;
  transition: border-color .12s, transform .12s;
}
.src-card:hover { border-color: var(--brand-200); transform: translateY(-1px); }
.src-head { display:flex; align-items:center; gap:8px; flex-wrap:wrap; }
.tag-fw {
  font-size: 11px; padding: 2px 7px; border-radius: 4px;
  background: var(--brand-50); color: var(--brand);
  border: 1px solid var(--brand-100); font-weight: 500;
}
.src-type { font-size: 11px; color: var(--fg-3); }
.src-score {
  margin-left:auto; font-size:11px; color: var(--brand);
  background: var(--brand-50); padding:2px 6px; border-radius:4px;
  font-variant-numeric: tabular-nums;
}
.src-title { font-size:13px; font-weight:600; color: var(--fg); }
.src-quote {
  font-size:12.5px; color: var(--fg-2); line-height:1.6;
  border-left: 2px solid var(--line-2); padding-left:10px;
}
.src-foot {
  display:flex; align-items:center; gap:6px;
  font-size:11px; color: var(--fg-4);
}

/* ================= RAGAS 进度条 (HTML 注入) ================= */
.ragas-grid { display:grid; grid-template-columns: 1fr 1fr 1fr; gap:14px; }
@media (max-width: 760px){ .ragas-grid { grid-template-columns: 1fr; } }
.ragas-row {
  background: var(--bg); border: 1px solid var(--line);
  border-radius: var(--r-md); padding: 12px;
}
.ragas-head { display:flex; align-items:baseline; justify-content:space-between; margin-bottom:8px; }
.ragas-label { font-size:11.5px; color: var(--fg-3); font-weight:500; }
.ragas-value { font-size:18px; font-weight:600; font-variant-numeric: tabular-nums; letter-spacing:-.01em; }
.ragas-pct   { font-size:11px; color: var(--fg-4); margin-left:2px; font-weight:500; }
.ragas-track { height:6px; border-radius:999px; background: var(--line); overflow:hidden; }
.ragas-fill  { height:100%; border-radius:999px; transition: width .4s ease; }
.ragas-high .ragas-fill { background: linear-gradient(90deg,#10B981,#059669); }
.ragas-high .ragas-value{ color:#047857; }
.ragas-mid  .ragas-fill { background: linear-gradient(90deg,#F59E0B,#D97706); }
.ragas-mid  .ragas-value{ color:#B45309; }
.ragas-low  .ragas-fill { background: linear-gradient(90deg,#F43F5E,#E11D48); }
.ragas-low  .ragas-value{ color:#BE123C; }

/* ================= chat_input (底部输入) ================= */
[data-testid="stChatInput"] {
  background: var(--surface) !important;
  border: 1px solid var(--line-2) !important;
  border-radius: var(--r-lg) !important;
  box-shadow: var(--shadow-md);
  padding: 4px 6px !important;
}
[data-testid="stChatInput"]:focus-within {
  border-color: var(--brand-3) !important;
  box-shadow: var(--shadow-md), 0 0 0 4px var(--brand-50) !important;
}
[data-testid="stChatInput"] textarea {
  font-size: 14px !important; line-height: 1.6 !important;
  background: transparent !important; border: 0 !important;
}
[data-testid="stChatInput"] button {
  background: var(--brand) !important;
  color: #fff !important;
  border-radius: 8px !important;
  border: 0 !important;
}
[data-testid="stChatInput"] button:hover { background: var(--brand-2) !important; }

/* 滚动条 */
*::-webkit-scrollbar { width: 8px; height: 8px; }
*::-webkit-scrollbar-thumb { background: var(--line-2); border-radius: 4px; }
*::-webkit-scrollbar-thumb:hover { background: var(--line-3); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)
```

---

## 3. 关键 HTML 片段（嵌在 Streamlit 里）

### 3.1 顶部标题区
```python
st.markdown(f"""
<div class="kb-topbar">
  <div>
    <h1 class="kb-title">AI 技术文档知识库</h1>
    <div class="kb-sub">基于 RAG 的文档问答 · 检索增强生成</div>
  </div>
  <div class="kb-status"><span class="dot"></span>向量库 · {len(docs)} 文档</div>
</div>

<div class="qa-title-row">
  <h2 class="qa-title">文档问答</h2>
  <span class="qa-pill">/ Ask</span>
</div>
""", unsafe_allow_html=True)
```

### 3.2 已上传文档行（侧边栏循环）
```python
for d in docs:
    c1, c2 = st.sidebar.columns([10, 2], gap="small")
    with c1:
        st.markdown(f"""
        <div class="doc-row">
          <div class="ico">📄</div>
          <div>
            <div class="name">{d['name']}</div>
            <div class="meta">
              <span class="tag-fw">{d['framework']}</span>
              <span>· {d['type']}</span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        if st.button("🗑", key=f"del_{d['id']}"):
            delete_doc(d['id'])
```

### 3.3 来源文档（在 expander 内）
```python
with st.expander(f"来源文档  · {len(sources)}", expanded=True):
    cards = "".join([f"""
      <div class="src-card">
        <div class="src-head">
          <span class="tag-fw">{s['framework']}</span>
          <span class="src-type">{s['type']}</span>
          <span class="src-score">相关度 {int(s['score']*100)}%</span>
        </div>
        <div class="src-title">{s['title']}</div>
        <div class="src-quote">{s['quote']}</div>
        <div class="src-foot">📄 {s['file']} · 第 {s['page']} 段</div>
      </div>
    """ for s in sources])
    st.markdown(f'<div class="src-grid">{cards}</div>', unsafe_allow_html=True)
```

### 3.4 RAGAS 评估分数
```python
def tier(v): return "high" if v >= 0.8 else "mid" if v >= 0.6 else "low"

def ragas_row(label, v):
    pct = int(v * 100)
    return f"""
    <div class="ragas-row ragas-{tier(v)}">
      <div class="ragas-head">
        <span class="ragas-label">{label}</span>
        <span class="ragas-value">{pct}<span class="ragas-pct">%</span></span>
      </div>
      <div class="ragas-track"><div class="ragas-fill" style="width:{pct}%"></div></div>
    </div>"""

with st.expander("RAGAS 评估分数", expanded=True):
    st.markdown(f"""
    <div class="ragas-grid">
      {ragas_row("Faithfulness · 忠实度",  ragas['faithfulness'])}
      {ragas_row("Answer Relevancy · 相关性", ragas['relevancy'])}
      {ragas_row("Context Precision · 准确度", ragas['precision'])}
    </div>
    """, unsafe_allow_html=True)
```

### 3.5 对话循环
```python
for m in st.session_state.messages:
    with st.chat_message(m["role"], avatar="✨" if m["role"]=="assistant" else "👤"):
        st.markdown(m["text"])
        if m["role"] == "assistant" and m.get("sources"):
            render_sources(m["sources"])
            render_ragas(m["ragas"])

prompt = st.chat_input("用中文提问，例如：LangGraph 怎么定义节点？")
```

---

## 4. 设计要点速查

| 维度 | 取值 |
|---|---|
| **主色** | `#4F46E5` (Indigo 600) |
| **背景** | `#FAFAFA` 主背景 / `#FFFFFF` 表面 / `#F4F4F5` 二级 |
| **文字** | `#18181B / #3F3F46 / #71717A / #A1A1AA` 四级 |
| **分隔线** | `#ECECEE` (主) / `#E4E4E7` (二级) |
| **圆角** | 6 / 10 / 14 / 18 |
| **字体** | Inter + Noto Sans SC，权重 400/500/600 |
| **小标题** | 11px · UPPERCASE · letter-spacing .08em · `--fg-4` |
| **正文** | 14px · 行高 1.7 |
| **大标题** | 22px · 600 · letter-spacing -.015em |
| **RAGAS 分级** | ≥80% 绿 · ≥60% 黄 · <60% 红 |
| **气泡** | user 靛蓝实心右下尖 / AI 白底 1px 描边左下尖 |
| **Tag** | 框架名用 `--brand-50` 底 + `--brand` 字 + `--brand-100` 边 |

完整可交互预览见 `index.html`。
