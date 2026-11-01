import { useCallback, useEffect, useState } from "react";
import { api } from "../services/api";

/** Loads documents and polls every 2s while any document is still processing. */
export function useDocuments() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setDocuments(await api.listDocuments());
    } catch {
      /* backend offline: banner is shown by AppContext */
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { refresh(); }, [refresh]);

  useEffect(() => {
    if (!documents.some((d) => d.status === "processing")) return;
    const t = setInterval(refresh, 2000);
    return () => clearInterval(t);
  }, [documents, refresh]);

  return { documents, loading, refresh };
}
