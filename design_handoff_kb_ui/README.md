# Handoff: AI 技术文档知识库 — Streamlit UI 重设计

## Overview
本设计稿是一个基于 RAG 的「AI 技术文档知识库」Streamlit 应用 UI 重设计。
主要功能：
- **左侧边栏**：上传 PDF/Markdown 文档（含框架名称、文档类型选择）；已上传文档列表（含删除按钮）
- **主区域**：顶部品牌渐变 banner + 文档问答对话区，含框架/类型过滤器
- **回答下方**：可折叠的「来源文档」（卡片+Tag 样式）和「RAGAS 评估分数」（三色进度条）

## About the Design Files
本目录中的 HTML/CSS/JSX 文件是**设计参考**——用 React + Babel 编写的高保真原型，用来展示视觉、布局、交互的最终效果。**不要直接拷贝代码运行**。

你的任务：
**把这套视觉移植到现有的 Streamlit 项目里**，通过 `st.markdown(unsafe_allow_html=True)` 注入 CSS、用 Streamlit 原生组件（`st.sidebar`, `st.file_uploader`, `st.chat_message`, `st.chat_input`, `st.expander` 等）搭建结构、并对接现有后端逻辑（上传/检索/RAGAS 调用）。

如果项目还没有 Streamlit 框架基础，先按 `streamlit-guide.md` 中的布局结构建立 `app.py`。

## Fidelity
**High-fidelity (hifi)**——所有颜色、字号、间距、阴影、渐变、圆角都已最终化，请严格按 `styles.css` 中的 design tokens 实现。

## Screens / Views

### 单一页面（双栏布局）

#### 1. 左侧边栏（296px 固定宽度）

**Layout**：
- 宽度 296px，高度 100vh，白底偏紫（`#F8F5FF`），右侧 1px 分隔线（`#E8E8F0`）
- 顶部 brand 区有浅紫渐变底（`linear-gradient(135deg, #F3F0FF 0%, #FDF4FF 50%, #FFF1F2 100%)`）
- 整体垂直布局：brand → 上传区 → 分隔线 → 已上传文档列表（flex:1 滚动）→ footer 状态条

**Components**：

| 组件 | 规格 |
|---|---|
| **Brand 区** | 高约 60px，左侧 4 块色 logo（22×22），右侧"知识库"渐变文字（15px/700）+ "KNOWLEDGE BASE" 副标（11px/uppercase/`#9494A8`） |
| **小标题** | 11px / 600 / uppercase / letter-spacing .08em / `#9494A8` |
| **Drop Zone** | 1px 虚线边（`#C9C9D6`），背景 `#EFEFF5`，圆角 10px；hover 时变 `linear-gradient` 浅紫底 + 实线边 `#A78BFA`；含上传图标 + "拖拽或点击上传" + "PDF · MD · 单文件 ≤ 200MB" |
| **输入框** | 高 34px，1px 边 `#DEDEE8`，圆角 6px，focus 时边变 `#8B5CF6` + 3px 紫色辉光 |
| **主按钮** | 高 36px，背景 `linear-gradient(135deg, #4F46E5, #7C3AED, #A855F7)`，白字，含 + 图标，box-shadow `0 6px 16px rgba(124,58,237,.28)`；disabled 时变灰 `#DEDEE8` |
| **文档行** | grid 22px / 1fr / auto；hover 时背景 `#EFEFF5`；左侧 22×22 文件图标块；中间文件名（12.5px/500）+ 框架 Tag + 类型；右侧删除按钮 hover 时显示玫红 |
| **框架 Tag** | 11px/600，背景 `linear-gradient(135deg, #F3F0FF, #EDE9FE)`，字 `#5B21B6`，边 `#C9BCFF`，圆角 4px |
| **Footer** | 顶部 1px 分隔线，绿色脉冲点 + "本地索引 · 已就绪"（11.5px / `#5E5E73`） |

#### 2. 主区域

**Layout**：垂直布局：topbar → qa-head → chat（flex:1 滚动）→ composer。

**Components**：

##### a. 顶部 Banner（`.topbar`，紧凑版）
- 高约 56px，padding `10px 28px`
- 背景：`linear-gradient(120deg, #4338CA 0%, #5B21B6 30%, #6D28D9 55%, #7C3AED 80%, #8B5CF6 100%)`
- 叠加两道光斑：`radial-gradient(500px 180px at 20% 50%, rgba(255,255,255,.20))` + `radial-gradient(400px 180px at 78% 60%, rgba(167,139,250,.30))`
- 标题：白色 15px/600，"AI 技术文档知识库"
- 副标：白色 82% 透明度，11.5px，"基于 RAG 的文档问答 · 检索增强生成"
- 右侧状态徽章：白色 18% 透明底 + 30% 透明边 + blur(8px) + 白色脉冲点 + "向量库 · N 文档"

##### b. QA Head 区（`.qa-head`）
- padding `14px 32px 10px`
- "文档问答" 大标题：22px / 600，`linear-gradient(180deg, #0F0F1A 30%, #5B21B6 100%)` 渐变文字
- 旁边 "/Ask" pill：11px 等宽字体，紫色渐变背景 + 白字
- 下方过滤器（grid 1fr / 240px）：
  - 框架 → 搜索图标 + input "留空则搜索全部"，圆角 10px
  - 文档类型 → 下拉，圆角 10px
  - 高度 36px，1px 边 `#DEDEE8`，focus 时紫色辉光

##### c. 对话区（`.chat`）
- padding `12px 32px 16px`，max-width 880px 居中
- 消息间距 22px
- **用户气泡**（右对齐）：紫色渐变 `linear-gradient(135deg, #4F46E5, #7C3AED, #A855F7)`，白字，圆角 14px / 右下角 4px，shadow `0 10px 28px rgba(124,58,237,.32)`；右侧 32×32 灰色用户头像
- **AI 气泡**（左对齐）：浅紫灰底 `#EFEFF5`，1px 边 `#E8E8F0`，圆角 14px / 左下角 4px；左侧有 3px 紫色渐变描边条
- **AI 头像**：32×32，紫色渐变 + 外发光光晕（filter:blur(10px) opacity:.35），白色 sparkle 图标

##### d. 折叠区（`.fold`）— 来源文档 / RAGAS
- 1px 边 `#E8E8F0`，圆角 10px
- 头部：12.5px/600 标题 + count pill + 右侧"点击展开/收起"
- **来源卡片**（双列 grid，gap 10px）：
  - 内含框架 Tag + 类型文字 + 右上角"相关度 92%"徽章（紫色渐变 + 白字）
  - 标题 13px/600
  - 引用文本 12.5px，左侧 2px 灰边作为引用条
  - 底部文件名 + 段号
  - hover 时边框变 `#A78BFA`，上移 1px，紫色淡阴影
- **RAGAS 卡片**（三列 grid）：
  - 白底，1px 边，圆角 10px，padding 14px
  - 左侧 3px 状态色条（与进度条同款三段渐变）
  - 顶部：标签（11.5px / `#5E5E73`） + 大数值（18px/600，三色之一）
  - 进度条：8px 高，圆角，三色渐变 + glow 阴影
  - 颜色分级：≥80% 绿（`#34D399→#10B981→#059669`）/ ≥60% 黄（`#FBBF24→#F59E0B→#D97706`）/ <60% 红（`#FB7185→#F43F5E→#E11D48`）

##### e. 输入框（`.composer`）
- padding `8px 32px 16px`，max-width 880px 居中
- 白底，1px 边 `#DEDEE8`，圆角 14px
- shadow `0 12px 32px rgba(124,58,237,.12)`
- focus 时显示渐变描边光环（mask 技术）+ 紫色辉光
- 内含 textarea + 底部行（左：键盘提示「↵ 发送 · ⇧↵ 换行」用 kbd 样式；右：30×30 send 按钮，激活时变紫色渐变实心）

## Interactions & Behavior

| 交互 | 实现 |
|---|---|
| **上传文档** | sidebar 的 file_uploader + 框架名 + 类型 → 点击"添加到知识库" → 调用后端持久化 → 刷新 session_state 中的 docs 列表 |
| **删除文档** | doc 行右侧按钮 → 后端删除 + session_state 同步 |
| **过滤** | 框架/类型 filter 改变时，下次问答时把过滤条件作为 metadata filter 传给检索器 |
| **提问** | `st.chat_input` 提交 → append user 消息 → 调用 RAG 链 → append AI 消息（含 sources + ragas）→ 自动滚到底 |
| **来源/RAGAS 折叠** | `st.expander` 默认 expanded=True，用户可手动收起 |
| **状态点呼吸动画** | `@keyframes pulse-dot` 2.4s ease-in-out infinite |
| **悬停效果** | 文档行 hover 显示删除按钮；来源卡片 hover 上浮 1px + 边色变 |

## State Management

Streamlit `st.session_state` 至少需要：
- `docs`: list[{id, name, framework, type}]
- `messages`: list[{role: "user"|"assistant", text, sources?, ragas?}]
- `filter_framework`: str
- `filter_type`: str

后端调用（**保留你现有的实现**）：
- 上传 → 解析 → 切片 → 向量化 → 写入 Qdrant
- 提问 → 按 filter 检索 → LLM 生成回答 → 调 RAGAS 评估 → 返回 {answer, sources, scores}

## Design Tokens

详见 `styles.css` 顶部 `:root` 块。核心值：

```css
/* Backgrounds */
--bg:        #F7F7FB;   /* main bg, 微冷紫调 */
--bg-2:      #EFEFF5;   /* AI 气泡底, drop zone */
--surface:   #FFFFFF;   /* cards, composer */
--sidebar-bg:#F8F5FF;   /* 侧边栏底色，轻紫 */

/* Lines */
--line:    #E8E8F0;
--line-2:  #DEDEE8;
--line-3:  #C9C9D6;

/* Text (4 级) */
--fg:    #0F0F1A;
--fg-2:  #2E2E40;
--fg-3:  #5E5E73;
--fg-4:  #9494A8;

/* Brand — Indigo / Violet */
--brand:    #4338CA;
--brand-2:  #6D28D9;
--brand-3:  #8B5CF6;
--accent:   #7C3AED;
--accent-2: #5B21B6;
--brand-50:  #F3F0FF;
--brand-100: #E5DEFF;
--brand-200: #C9BCFF;
--brand-300: #A78BFA;

/* 核心渐变 */
--grad-1:      linear-gradient(135deg, #4F46E5 0%, #7C3AED 50%, #A855F7 100%);
--grad-2:      linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
--grad-aurora: linear-gradient(120deg, #4338CA 0%, #5B21B6 30%, #6D28D9 55%, #7C3AED 80%, #8B5CF6 100%); /* 顶部 banner 专用 */

/* RAGAS 三色 */
--green: #10B981;   /* ≥80% */
--amber: #F59E0B;   /* ≥60% */
--rose:  #F43F5E;   /* <60% */

/* Radii */
6px / 10px / 14px / 18px

/* Shadows */
sm: 0 1px 2px rgba(24,24,27,.04), 0 0 0 1px rgba(24,24,27,.04)
md: 0 4px 16px rgba(24,24,27,.06), 0 0 0 1px rgba(24,24,27,.05)
brand-glow: 0 12px 32px rgba(124,58,237,.12)

/* Typography */
font-family: "Inter", "Noto Sans SC", -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif
正文 14px / line-height 1.7
小标题 11px / 600 / uppercase / letter-spacing .08em
大标题 22px / 600 / letter-spacing -.015em
```

## Assets
- **字体**：Google Fonts — Inter (400/500/600/700) + Noto Sans SC (400/500/600/700) + JetBrains Mono (400/500)
- **图标**：全部 inline SVG（在 `app.jsx` 顶部 `Icon` 对象里），可改用 `streamlit-extras` 或者 emoji 替代
- **图片**：无（所有视觉元素均为 CSS）

## Files

| 文件 | 用途 |
|---|---|
| `index.html` | 完整可交互的 React 原型入口 |
| `app.jsx` | React 组件源码（Sidebar / Filters / MessageBubble / SourceCard / RagasBar / Composer） |
| `styles.css` | **核心** — 所有 design tokens + 组件样式（742 行） |
| `streamlit-guide.md` | **核心** — Streamlit 适配指南：完整 CSS 注入代码 + HTML 片段（顶部标题、文档行、来源卡、RAGAS、对话循环） |
| `README.md` | 本文档 |

## 实施建议步骤（给开发者）

1. **跑起来看效果**：双击 `index.html` 在浏览器打开，体验最终视觉与交互
2. **读 tokens**：打开 `styles.css` 顶部 `:root`，把所有变量原样拷贝到你 Streamlit 项目里
3. **读 streamlit-guide.md**：里面有可直接 `st.markdown(CSS, unsafe_allow_html=True)` 注入的完整 CSS 块
4. **按结构搭页面**：`st.set_page_config(layout="wide")` → 注入 CSS → 用 `st.sidebar` + `st.chat_message` + `st.expander` 拼出布局
5. **对接后端**：保留你现有的上传/检索/RAGAS 函数，只替换 UI 层
6. **细节验证**：对照 `index.html` 检查圆角、阴影、字号、渐变是否一致

如有疑问，逐个组件对照 `app.jsx` 里的 JSX 结构找到对应 className，再在 `styles.css` 中查找选择器。
