import { Link } from "react-router-dom";
import { useApp } from "../context/AppContext.jsx";
import UploadBox from "../components/UploadBox.jsx";

export default function Dashboard() {
  const { documents, health } = useApp();
  const ready = documents.filter((d) => d.status === "ready");
  const stats = [
    ["Documents", documents.length],
    ["Ready", ready.length],
    ["Total pages", ready.reduce((n, d) => n + d.pages, 0)],
    ["Text chunks", ready.reduce((n, d) => n + d.chunk_count, 0)],
  ];
  return (
    <div className="mx-auto max-w-4xl space-y-6">
      <h1 className="text-2xl font-bold">AI PDF Question Answering</h1>
      <p className="text-sm text-slate-600 dark:text-slate-300">
        Upload PDFs, then ask questions. Answers come from retrieved passages and always show their page references.
        {health && <> Current answer mode: <b>{health.answer_mode === "llm" ? `LLM (${health.llm_provider})` : "local extractive (no LLM key configured)"}</b>.</>}
      </p>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {stats.map(([label, value]) => (
          <div key={label} className="card"><p className="text-2xl font-bold text-indigo-600">{value}</p><p className="text-xs text-slate-500">{label}</p></div>
        ))}
      </div>
      <UploadBox />
      <div className="flex gap-3">
        <Link className="btn" to="/chat">Start chatting</Link>
        <Link className="btn-ghost" to="/documents">Manage documents</Link>
      </div>
    </div>
  );
}
