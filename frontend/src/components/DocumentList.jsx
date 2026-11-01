import { useState } from "react";
import { FileText, MessageSquare, Sparkles, Trash2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import StatusBadge from "./StatusBadge.jsx";
import SummaryModal from "./SummaryModal.jsx";
import { api, errorMessage } from "../services/api";
import { useApp } from "../context/AppContext.jsx";

export default function DocumentList({ documents }) {
  const { refresh } = useApp();
  const navigate = useNavigate();
  const [summaryDoc, setSummaryDoc] = useState(null);
  const [error, setError] = useState("");

  async function remove(doc) {
    if (!window.confirm(`Delete "${doc.filename}" and its embeddings?`)) return;
    try { await api.deleteDocument(doc.id); refresh(); } catch (e) { setError(errorMessage(e)); }
  }
  async function chat(doc) {
    try { const c = await api.createConversation([doc.id]); navigate(`/chat/${c.id}`); } catch (e) { setError(errorMessage(e)); }
  }

  if (!documents.length) return <p className="text-sm text-slate-500">No documents yet. Upload a PDF to get started.</p>;
  return (
    <>
      {error && <p className="mb-2 text-sm text-red-600">{error}</p>}
      <ul className="space-y-3">
        {documents.map((d) => (
          <li key={d.id} className="card flex flex-wrap items-center justify-between gap-3">
            <div className="flex min-w-0 items-center gap-3">
              <FileText className="shrink-0 text-indigo-500" />
              <div className="min-w-0">
                <p className="truncate font-medium">{d.filename}</p>
                <p className="text-xs text-slate-500">
                  {(d.size_bytes / 1024).toFixed(0)} KB
                  {d.status === "ready" && ` · ${d.pages} pages · ${d.chunk_count} chunks`} · <StatusBadge status={d.status} />
                </p>
                {d.status === "failed" && <p className="mt-1 text-xs text-red-600">{d.error}</p>}
              </div>
            </div>
            <div className="flex gap-2">
              <button className="btn-ghost" disabled={d.status !== "ready"} onClick={() => setSummaryDoc(d)}><Sparkles size={14} /> Summary</button>
              <button className="btn" disabled={d.status !== "ready"} onClick={() => chat(d)}><MessageSquare size={14} /> Chat</button>
              <button className="btn-ghost text-red-600" onClick={() => remove(d)} aria-label="Delete"><Trash2 size={14} /></button>
            </div>
          </li>
        ))}
      </ul>
      {summaryDoc && <SummaryModal doc={summaryDoc} onClose={() => { setSummaryDoc(null); refresh(); }} />}
    </>
  );
}
