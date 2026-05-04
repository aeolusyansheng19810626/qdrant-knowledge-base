const { useState, useRef, useEffect } = React;

/* ---------- Icons ---------- */
const Icon = {
  Logo: (p) => (
    <svg viewBox="0 0 24 24" width="22" height="22" fill="none" {...p}>
      <rect x="3" y="3" width="8" height="8" rx="2" fill="#4F46E5"/>
      <rect x="13" y="3" width="8" height="8" rx="2" fill="#818CF8"/>
      <rect x="3" y="13" width="8" height="8" rx="2" fill="#A5B4FC"/>
      <rect x="13" y="13" width="8" height="8" rx="2" fill="#4F46E5"/>
    </svg>
  ),
  Upload: (p) => (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M12 16V4M6 10l6-6 6 6"/>
      <path d="M4 18v2a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-2"/>
    </svg>
  ),
  Send: (p) => (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M5 12h14M13 6l6 6-6 6"/>
    </svg>
  ),
  Search: (p) => (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/>
    </svg>
  ),
  Trash: (p) => (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M3 6h18M8 6V4a1 1 0 0 1 1-1h6a1 1 0 0 1 1 1v2M6 6l1 14a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-14M10 11v6M14 11v6"/>
    </svg>
  ),
  File: (p) => (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5"/>
    </svg>
  ),
  Chevron: (p) => (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="m6 9 6 6 6-6"/>
    </svg>
  ),
  User: (p) => (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <circle cx="12" cy="8" r="4"/><path d="M4 21a8 8 0 0 1 16 0"/>
    </svg>
  ),
  Sparkle: (p) => (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M12 3v4M12 17v4M3 12h4M17 12h4M5.6 5.6l2.8 2.8M15.6 15.6l2.8 2.8M5.6 18.4l2.8-2.8M15.6 8.4l2.8-2.8"/>
    </svg>
  ),
  Plus: (p) => (
    <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M12 5v14M5 12h14"/>
    </svg>
  ),
  Check: (p) => (
    <svg viewBox="0 0 24 24" width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" {...p}>
      <path d="M5 13l4 4L19 7"/>
    </svg>
  ),
};

/* ---------- Sidebar ---------- */
function Sidebar({ docs, onUpload, onDelete }) {
  const [framework, setFramework] = useState("");
  const [docType, setDocType] = useState("教程");
  const [filename, setFilename] = useState("");
  const [hover, setHover] = useState(false);

  const submit = () => {
    if (!filename || !framework) return;
    onUpload({ name: filename, framework, type: docType });
    setFilename("");
  };

  return (
    <aside className="sidebar">
      <div className="brand">
        <Icon.Logo />
        <div className="brand-text">
          <div className="brand-title">知识库</div>
          <div className="brand-sub">Knowledge Base</div>
        </div>
      </div>

      <div className="side-section">
        <div className="side-label">上传文档</div>

        <label
          className={`drop ${hover ? "drop-hover" : ""}`}
          onDragOver={(e) => { e.preventDefault(); setHover(true); }}
          onDragLeave={() => setHover(false)}
          onDrop={(e) => { e.preventDefault(); setHover(false); if (e.dataTransfer.files[0]) setFilename(e.dataTransfer.files[0].name); }}
        >
          <div className="drop-icon"><Icon.Upload /></div>
          <div className="drop-title">拖拽或点击上传</div>
          <div className="drop-meta">PDF · MD · 单文件 ≤ 200MB</div>
          <input
            type="text"
            className="drop-fake"
            placeholder=" "
            value={filename}
            onChange={(e) => setFilename(e.target.value)}
          />
          {filename && (
            <div className="drop-file">
              <Icon.File /> <span>{filename}</span>
            </div>
          )}
        </label>

        <div className="field">
          <label className="field-label">框架名称</label>
          <input
            className="input"
            placeholder="例如：LangChain、Qdrant"
            value={framework}
            onChange={(e) => setFramework(e.target.value)}
          />
        </div>

        <div className="field">
          <label className="field-label">文档类型</label>
          <div className="select-wrap">
            <select className="input" value={docType} onChange={(e) => setDocType(e.target.value)}>
              <option>教程</option>
              <option>API 文档</option>
              <option>白皮书</option>
              <option>博客</option>
              <option>源码注释</option>
            </select>
            <Icon.Chevron className="select-chev" />
          </div>
        </div>

        <button
          className={`btn-primary ${(!filename || !framework) ? "btn-disabled" : ""}`}
          onClick={submit}
        >
          <Icon.Plus /> 添加到知识库
        </button>
      </div>

      <div className="side-divider"/>

      <div className="side-section grow">
        <div className="side-label">
          <span>已上传文档</span>
          <span className="count-pill">{docs.length}</span>
        </div>

        <div className="doc-list">
          {docs.map((d) => (
            <div className="doc-row" key={d.id}>
              <div className="doc-row-icon"><Icon.File /></div>
              <div className="doc-row-body">
                <div className="doc-row-name" title={d.name}>{d.name}</div>
                <div className="doc-row-meta">
                  <span className="tag tag-fw">{d.framework}</span>
                  <span className="dot-sep">·</span>
                  <span className="doc-row-type">{d.type}</span>
                </div>
              </div>
              <button className="icon-btn" onClick={() => onDelete(d.id)} aria-label="删除">
                <Icon.Trash />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="side-foot">
        <div className="foot-dot"/> <span>本地索引 · 已就绪</span>
      </div>
    </aside>
  );
}

/* ---------- Filters ---------- */
function Filters({ frameworks, types, fw, setFw, ty, setTy }) {
  return (
    <div className="filters">
      <div className="filter">
        <div className="filter-label">框架</div>
        <div className="filter-search">
          <Icon.Search />
          <input
            className="filter-input"
            placeholder="留空则搜索全部"
            value={fw}
            onChange={(e) => setFw(e.target.value)}
            list="fw-list"
          />
          <datalist id="fw-list">
            {frameworks.map((f) => <option key={f} value={f}/>)}
          </datalist>
        </div>
      </div>
      <div className="filter">
        <div className="filter-label">文档类型</div>
        <div className="select-wrap">
          <select className="filter-input filter-select" value={ty} onChange={(e) => setTy(e.target.value)}>
            <option>全部</option>
            {types.map((t) => <option key={t}>{t}</option>)}
          </select>
          <Icon.Chevron className="select-chev" />
        </div>
      </div>
    </div>
  );
}

/* ---------- RAGAS Bar ---------- */
function RagasBar({ label, value }) {
  // value 0..1
  const pct = Math.round(value * 100);
  const tier = value >= 0.8 ? "high" : value >= 0.6 ? "mid" : "low";
  return (
    <div className={`ragas-row ragas-${tier}`}>
      <div className="ragas-head">
        <span className="ragas-label">{label}</span>
        <span className="ragas-value">{pct}<span className="ragas-pct">%</span></span>
      </div>
      <div className="ragas-track">
        <div className="ragas-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}

/* ---------- Source Card ---------- */
function SourceCard({ s }) {
  return (
    <div className="src-card">
      <div className="src-head">
        <span className="tag tag-fw">{s.framework}</span>
        <span className="src-type">{s.type}</span>
        <span className="src-score">相关度 {Math.round(s.score*100)}%</span>
      </div>
      <div className="src-title">{s.title}</div>
      <div className="src-quote">{s.quote}</div>
      <div className="src-foot">
        <Icon.File /> <span className="src-file">{s.file}</span>
        <span className="src-loc">第 {s.page} 段</span>
      </div>
    </div>
  );
}

/* ---------- Message ---------- */
function MessageBubble({ m }) {
  const [openSrc, setOpenSrc] = useState(true);
  const [openRagas, setOpenRagas] = useState(true);

  if (m.role === "user") {
    return (
      <div className="msg msg-user">
        <div className="bubble bubble-user">{m.text}</div>
        <div className="avatar avatar-user"><Icon.User /></div>
      </div>
    );
  }

  return (
    <div className="msg msg-ai">
      <div className="avatar avatar-ai"><Icon.Sparkle /></div>
      <div className="bubble bubble-ai">
        <div className="bubble-text">
          {m.text.split("\n").map((p, i) => <p key={i}>{p}</p>)}
        </div>

        {m.sources && (
          <div className={`fold ${openSrc ? "fold-open" : ""}`}>
            <button className="fold-head" onClick={() => setOpenSrc(!openSrc)}>
              <Icon.Chevron className={`fold-chev ${openSrc ? "rot" : ""}`} />
              <span className="fold-title">来源文档</span>
              <span className="count-pill">{m.sources.length}</span>
              <span className="fold-spacer"/>
              <span className="fold-meta">点击展开 / 收起</span>
            </button>
            {openSrc && (
              <div className="fold-body">
                <div className="src-grid">
                  {m.sources.map((s, i) => <SourceCard key={i} s={s} />)}
                </div>
              </div>
            )}
          </div>
        )}

        {m.ragas && (
          <div className={`fold ${openRagas ? "fold-open" : ""}`}>
            <button className="fold-head" onClick={() => setOpenRagas(!openRagas)}>
              <Icon.Chevron className={`fold-chev ${openRagas ? "rot" : ""}`} />
              <span className="fold-title">RAGAS 评估分数</span>
              <span className={`ragas-overall ragas-${m.ragas.faithfulness >= 0.8 ? "high" : "mid"}`}>
                综合 {Math.round((m.ragas.faithfulness + m.ragas.relevancy + m.ragas.precision)/3*100)}
              </span>
              <span className="fold-spacer"/>
            </button>
            {openRagas && (
              <div className="fold-body">
                <div className="ragas-grid">
                  <RagasBar label="Faithfulness · 忠实度" value={m.ragas.faithfulness} />
                  <RagasBar label="Answer Relevancy · 相关性" value={m.ragas.relevancy} />
                  <RagasBar label="Context Precision · 准确度" value={m.ragas.precision} />
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

/* ---------- Composer ---------- */
function Composer({ onSend }) {
  const [val, setVal] = useState("");
  const ref = useRef(null);

  const send = () => {
    if (!val.trim()) return;
    onSend(val.trim());
    setVal("");
  };
  const onKey = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  };

  return (
    <div className="composer-wrap">
      <div className="composer">
        <textarea
          ref={ref}
          className="composer-input"
          placeholder="用中文提问，例如：LangGraph 怎么定义节点？"
          value={val}
          onChange={(e) => setVal(e.target.value)}
          onKeyDown={onKey}
          rows={1}
        />
        <div className="composer-foot">
          <div className="composer-hints">
            <span className="kbd">↵</span> 发送 ·
            <span className="kbd">⇧↵</span> 换行
          </div>
          <button className={`send-btn ${val.trim() ? "send-btn-active" : ""}`} onClick={send}>
            <Icon.Send />
          </button>
        </div>
      </div>
    </div>
  );
}

/* ---------- Main App ---------- */
function App() {
  const [docs, setDocs] = useState([
    { id: 1, name: "LangChain-Cookbook-2026.pdf", framework: "LangChain", type: "教程" },
    { id: 2, name: "LangGraph-API-Reference.md", framework: "LangGraph", type: "API 文档" },
    { id: 3, name: "qdrant-vector-search-guide.pdf", framework: "Qdrant", type: "教程" },
    { id: 4, name: "Ollama-Deployment-Notes.md", framework: "Ollama", type: "博客" },
  ]);

  const [fw, setFw] = useState("");
  const [ty, setTy] = useState("全部");

  const [messages, setMessages] = useState([
    {
      role: "user",
      text: "langchain 和 langgraph 的区分是什么？什么场景下应该用哪个？",
    },
    {
      role: "ai",
      text:
        "LangChain 和 LangGraph 是两个相关但定位不同的框架，都用于基于大语言模型（LLMs）的应用开发。\n• LangChain 是一个通用的应用开发框架，提供了一系列工具与组件（Prompt、Memory、Tool、Agent、Retriever 等），让开发者能快速搭建基于 LLM 的应用，强调链式（chain）组合。\n• LangGraph 在 LangChain 基础上构建，是一个图（graph）计算框架，主要用于管理与编排带状态的 Agent 工作流，支持显式节点、边、循环与持久化。\n选用建议：单轮 / 简单顺序流程 → LangChain；多轮、需要回路与状态管理的复杂 Agent → LangGraph。",
      sources: [
        { framework: "LangChain", type: "教程", score: 0.92, title: "LangChain 概述与核心抽象", quote: "LangChain 提供 Prompt、Memory、Tool、Retriever 等可组合的原语，用于构建链式 LLM 应用…", file: "LangChain-Cookbook-2026.pdf", page: 3 },
        { framework: "LangGraph", type: "API 文档", score: 0.88, title: "Why LangGraph", quote: "LangGraph 在 LangChain 之上提供基于图的状态机模型，用于构建可循环、可恢复的 Agent…", file: "LangGraph-API-Reference.md", page: 1 },
        { framework: "LangGraph", type: "教程", score: 0.74, title: "Graph vs Chain", quote: "Chain 适合线性顺序工作流；Graph 适合多分支、含回路、需要状态持久化的工作流。", file: "LangGraph-API-Reference.md", page: 7 },
      ],
      ragas: { faithfulness: 0.91, relevancy: 0.84, precision: 0.72 },
    },
  ]);

  const onUpload = (d) => setDocs([{ id: Date.now(), ...d }, ...docs]);
  const onDelete = (id) => setDocs(docs.filter((x) => x.id !== id));

  const onSend = (text) => {
    const next = [...messages, { role: "user", text }];
    setMessages(next);
    // simulated ai
    setTimeout(() => {
      setMessages((cur) => [...cur, {
        role: "ai",
        text: "已根据你的知识库检索相关文档并生成回答。\n建议：先用「框架」过滤器锁定范围，可以显著提升准确度（Context Precision）。",
        sources: [
          { framework: "LangChain", type: "教程", score: 0.86, title: "Retriever Best Practices", quote: "为获得更高的准确度，推荐先按元数据进行硬过滤，再做向量召回…", file: "LangChain-Cookbook-2026.pdf", page: 18 },
          { framework: "Qdrant", type: "教程", score: 0.79, title: "Payload Filtering", quote: "Qdrant 支持在 payload 上进行结构化过滤，与向量检索联合使用以提升精度。", file: "qdrant-vector-search-guide.pdf", page: 5 },
        ],
        ragas: { faithfulness: 0.86, relevancy: 0.81, precision: 0.78 },
      }]);
    }, 350);
  };

  const frameworks = Array.from(new Set(docs.map((d) => d.framework)));
  const types = Array.from(new Set(docs.map((d) => d.type)));

  // auto scroll
  const scrollRef = useRef(null);
  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  return (
    <div className="shell">
      <Sidebar docs={docs} onUpload={onUpload} onDelete={onDelete} />
      <main className="main">
        <header className="topbar">
          <div className="topbar-left">
            <h1 className="page-title">AI 技术文档知识库</h1>
            <div className="page-sub">基于 RAG 的文档问答 · 检索增强生成</div>
          </div>
          <div className="topbar-right">
            <div className="status">
              <span className="status-dot"/>
              <span>向量库 · {docs.length} 文档</span>
            </div>
          </div>
        </header>

        <section className="qa-head">
          <div className="qa-title-row">
            <h2 className="qa-title">文档问答</h2>
            <div className="qa-pill">/ Ask</div>
          </div>
          <Filters
            frameworks={frameworks}
            types={types}
            fw={fw} setFw={setFw}
            ty={ty} setTy={setTy}
          />
        </section>

        <section className="chat" ref={scrollRef}>
          <div className="chat-inner">
            {messages.map((m, i) => <MessageBubble key={i} m={m} />)}
          </div>
        </section>

        <Composer onSend={onSend} />
      </main>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App/>);
