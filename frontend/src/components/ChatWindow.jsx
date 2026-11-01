import { useEffect, useRef, useState } from "react";
import { Bot, ChevronDown, Send, User } from "lucide-react";

function Sources({ sources }) {
  const [open, setOpen] = useState(false);
  if (!sources?.length) return null;
  return (
    <div className="mt-2 text-xs">
      <button className="flex items-center gap-1 text-indigo-600" onClick={() => setOpen(!open)}>
        <ChevronDown size={12} className={open ? "rotate-180" : ""} /> {sources.length} source{sources.length > 1 ? "s" : ""}
      </button>
      <div className="mt-1 flex flex-wrap gap-1">
        {sources.map((s, i) => (
          <span key={i} className="rounded bg-slate-100 px-2 py-0.5 dark:bg-slate-700">{s.filename} · p.{s.page}</span>
        ))}
      </div>
      {open && sources.map((s, i) => (
        <blockquote key={i} className="mt-2 border-l-2 border-indigo-300 pl-2 text-slate-600 dark:text-slate-300">
          <b>{s.filename}, p.{s.page}</b> (similarity {s.score}): {s.text.slice(0, 500)}{s.text.length > 500 && "…"}
        </blockquote>
      ))}
    </div>
  );
}

const MODE_LABEL = { llm: "LLM answer", extractive: "Extractive (no LLM)", no_evidence: "No evidence", error: "Error" };

export default function ChatWindow({ messages, onSend, sending, disabled }) {
  const [text, setText] = useState("");
  const [mode, setMode] = useState("auto");
  const end = useRef(null);
  useEffect(() => { end.current?.scrollIntoView({ behavior: "smooth" }); }, [messages, sending]);

  function submit(e) {
    e.preventDefault();
    if (!text.trim() || sending || disabled) return;
    onSend(text.trim(), mode);
    setText("");
  }

  return (
    <div className="card flex h-[70vh] flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {!messages.length && <p className="text-sm text-slate-500">Ask a question about the selected document(s).</p>}
        {messages.map((m, i) => (
          <div key={m.id ?? i} className={`flex gap-2 ${m.role === "user" ? "justify-end" : ""}`}>
            {m.role !== "user" && <Bot className="mt-1 shrink-0 text-indigo-500" size={18} />}
            <div className={`max-w-[85%] rounded-xl px-3 py-2 text-sm ${m.role === "user" ? "bg-indigo-600 text-white" : "bg-slate-100 dark:bg-slate-700"}`}>
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.role !== "user" && m.mode && <p className="mt-1 text-[11px] opacity-60">{MODE_LABEL[m.mode] || m.mode}</p>}
              {m.role !== "user" && <Sources sources={m.sources} />}
            </div>
            {m.role === "user" && <User className="mt-1 shrink-0" size={18} />}
          </div>
        ))}
        {sending && <p className="text-sm text-slate-500">Searching the document…</p>}
        <div ref={end} />
      </div>
      <form onSubmit={submit} className="mt-3 flex gap-2">
        <select value={mode} onChange={(e) => setMode(e.target.value)} className="rounded-lg border border-slate-300 bg-transparent px-2 text-sm dark:border-slate-600" title="Answer mode">
          <option value="auto">Auto</option><option value="llm">LLM only</option><option value="extractive">Extractive only</option>
        </select>
        <input value={text} onChange={(e) => setText(e.target.value)} disabled={disabled} maxLength={2000}
          placeholder="Ask a question…" className="flex-1 rounded-lg border border-slate-300 bg-transparent px-3 py-2 text-sm dark:border-slate-600" />
        <button className="btn" disabled={sending || disabled}><Send size={14} /> Send</button>
      </form>
    </div>
  );
}
