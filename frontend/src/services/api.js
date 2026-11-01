import axios from "axios";

const http = axios.create({ baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000", timeout: 120000 });

export function errorMessage(err) {
  if (err.response) return err.response.data?.detail || `Request failed (${err.response.status})`;
  return "Cannot reach the backend. Is it running and is VITE_API_URL correct?";
}

export const api = {
  health: () => http.get("/api/health").then((r) => r.data),
  listDocuments: () => http.get("/api/documents").then((r) => r.data),
  uploadDocument: (file) => {
    const form = new FormData();
    form.append("file", file);
    return http.post("/api/documents", form).then((r) => r.data);
  },
  deleteDocument: (id) => http.delete(`/api/documents/${id}`).then((r) => r.data),
  summarize: (id) => http.post(`/api/documents/${id}/summarize`).then((r) => r.data),
  listConversations: () => http.get("/api/conversations").then((r) => r.data),
  createConversation: (document_ids) => http.post("/api/conversations", { document_ids }).then((r) => r.data),
  getConversation: (id) => http.get(`/api/conversations/${id}`).then((r) => r.data),
  deleteConversation: (id) => http.delete(`/api/conversations/${id}`).then((r) => r.data),
  clearConversation: (id) => http.post(`/api/conversations/${id}/clear`).then((r) => r.data),
  ask: (id, question, mode) => http.post(`/api/conversations/${id}/ask`, { question, mode }).then((r) => r.data),
};
