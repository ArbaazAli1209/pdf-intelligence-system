import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Eraser, Plus, Trash2 } from "lucide-react";
import ChatWindow from "../components/ChatWindow.jsx";
import { api, errorMessage } from "../services/api";
import { useApp } from "../context/AppContext.jsx";

export default function Chat() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { documents } = useApp();
  const readyDocs = documents.filter((d) => d.status === "ready");
  const [conversations, setConversations] = useState([]);
  const [conv, setConv] = useState(null);
  const [selected, setSelected] = useState([]);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState("");

  const loadList = useCallback(() => api.listConversations().then(setConversations).catch(() => {}), []);
  useEffect(() => { loadList(); }, [loadList]);

  useEffect(() => {
    setError("");
    if (!id) { setConv(null); return; }
    api.getConversation(id).then(setConv).catch((e) => { setError(errorMessage(e)); setConv(null); });
  }, [id]);

  async function newChat() {
    if (!selected.length) { setError("Select at least one ready document first."); return; }
    try { const c = await api.createConversation(selected); await loadList(); navigate(`/chat/${c.id}`); setError(""); }
    catch (e) { setError(errorMessage(e)); }
  }

  async function send(question, mode) {
    setError(""); setSending(true);
    setConv((c) => ({ ...c, messages: [...c.messages, { role: "user", content: question }] }));
    try {
      const reply = await api.ask(conv.id, question, mode);
      setConv((c) => ({ ...c, messages: [...c.messages, reply] }));
      loadList();
    } catch (e) { setError(errorMessage(e)); }
    setSending(false);
  }

  async function clear() { await api.clearConversation(conv.id); setConv({ ...conv, messages: [] }); }
  async function remove(cid) {
    await api.deleteConversation(cid); await loadList();
    if (String(cid) === String(id)) navigate("/chat");
  }
  const toggle = (docId) => setSelected((s) => (s.includes(docId) ? s.filter((x) => x !== docId) : [...s, docId]));
  const names = conv ? documents.filter((d) => conv.document_ids.includes(d.id)).map((d) => d.filename) : [];

  return (
    <div className="mx-auto grid max-w-6xl gap-6 lg:grid-cols-[18rem_1fr]">
      <div className="space-y-4">
        <div className="card">
          <h2 className="mb-2 text-sm font-semibold">New conversation</h2>
          {!readyDocs.length && <p className="text-xs text-slate-500">Upload and process a PDF first.</p>}
          <div className="max-h-40 space-y-1 overflow-y-auto">
            {readyDocs.map((d) => (
              <label key={d.id} className="flex items-center gap-2 text-sm">
                <input type="checkbox" checked={selected.includes(d.id)} onChange={() => toggle(d.id)} />
                <span className="truncate">{d.filename}</span>
              </label>
            ))}
          </div>
          <button className="btn mt-3 w-full justify-center" onClick={newChat}><Plus size={14} /> Start</button>
        </div>
        <div className="card">
          <h2 className="mb-2 text-sm font-semibold">History</h2>
          {!conversations.length && <p className="text-xs text-slate-500">No conversations yet.</p>}
          <ul className="space-y-1">
            {conversations.map((c) => (
              <li key={c.id} className={`flex items-center justify-between rounded px-2 py-1 text-sm ${String(c.id) === String(id) ? "bg-indigo-50 dark:bg-slate-700" : ""}`}>
                <button className="truncate text-left" onClick={() => navigate(`/chat/${c.id}`)}>{c.title}</button>
                <button onClick={() => remove(c.id)} aria-label="Delete conversation"><Trash2 size={13} /></button>
              </li>
            ))}
          </ul>
        </div>
      </div>
      <div className="space-y-3">
        {error && <p className="rounded-lg bg-red-50 p-2 text-sm text-red-700 dark:bg-red-950 dark:text-red-200">{error}</p>}
        {conv ? (
          <>
            <div className="flex items-center justify-between text-sm">
              <span className="truncate text-slate-500">Documents: {names.join(", ") || "(deleted)"}</span>
              <button className="btn-ghost" onClick={clear}><Eraser size={14} /> Clear</button>
            </div>
            <ChatWindow messages={conv.messages} onSend={send} sending={sending} disabled={!names.length} />
          </>
        ) : (
          <div className="card text-sm text-slate-500">Select document(s) and start a conversation, or open one from the history.</div>
        )}
      </div>
    </div>
  );
}
