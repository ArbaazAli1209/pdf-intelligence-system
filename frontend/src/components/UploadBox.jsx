import { useRef, useState } from "react";
import { UploadCloud } from "lucide-react";
import { api, errorMessage } from "../services/api";
import { useApp } from "../context/AppContext.jsx";

const MAX_MB = 20; // keep in sync with backend MAX_UPLOAD_MB

export default function UploadBox() {
  const { refresh } = useApp();
  const input = useRef(null);
  const [busy, setBusy] = useState(false);
  const [errors, setErrors] = useState([]);

  async function handleFiles(fileList) {
    const errs = [];
    setBusy(true);
    for (const file of Array.from(fileList)) {
      if (!file.name.toLowerCase().endsWith(".pdf")) { errs.push(`${file.name}: only PDF files are allowed.`); continue; }
      if (file.size > MAX_MB * 1024 * 1024) { errs.push(`${file.name}: larger than ${MAX_MB} MB.`); continue; }
      try { await api.uploadDocument(file); } catch (e) { errs.push(`${file.name}: ${errorMessage(e)}`); }
    }
    setErrors(errs);
    setBusy(false);
    refresh();
    if (input.current) input.current.value = "";
  }

  return (
    <div className="card">
      <div
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => { e.preventDefault(); handleFiles(e.dataTransfer.files); }}
        onClick={() => input.current?.click()}
        className="flex cursor-pointer flex-col items-center gap-2 rounded-lg border-2 border-dashed border-slate-300 p-8 text-center hover:border-indigo-400 dark:border-slate-600"
      >
        <UploadCloud size={32} className="text-indigo-500" />
        <p className="text-sm">{busy ? "Uploading…" : "Drag & drop PDFs here, or click to browse"}</p>
        <p className="text-xs text-slate-500">Text-based PDFs up to {MAX_MB} MB. Scanned PDFs need OCR (not included).</p>
        <input ref={input} type="file" accept="application/pdf,.pdf" multiple hidden onChange={(e) => handleFiles(e.target.files)} />
      </div>
      {errors.length > 0 && (
        <ul className="mt-3 space-y-1 text-sm text-red-600">{errors.map((e) => <li key={e}>{e}</li>)}</ul>
      )}
    </div>
  );
}
