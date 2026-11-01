import UploadBox from "../components/UploadBox.jsx";
import DocumentList from "../components/DocumentList.jsx";
import { useApp } from "../context/AppContext.jsx";

export default function Documents() {
  const { documents, loading } = useApp();
  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold">Documents</h1>
      <UploadBox />
      {loading ? <p className="text-sm">Loading…</p> : <DocumentList documents={documents} />}
    </div>
  );
}
