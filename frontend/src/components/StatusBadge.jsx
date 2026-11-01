import { CheckCircle2, Loader2, XCircle } from "lucide-react";

export default function StatusBadge({ status }) {
  if (status === "ready") return <span className="inline-flex items-center gap-1 text-xs text-green-600"><CheckCircle2 size={14} /> Ready</span>;
  if (status === "failed") return <span className="inline-flex items-center gap-1 text-xs text-red-600"><XCircle size={14} /> Failed</span>;
  return <span className="inline-flex items-center gap-1 text-xs text-amber-600"><Loader2 size={14} className="animate-spin" /> Processing</span>;
}
