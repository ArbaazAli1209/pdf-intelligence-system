import { createContext, useContext, useEffect, useState } from "react";
import { api } from "../services/api";
import { useDocuments } from "../hooks/useDocuments";

const AppContext = createContext(null);
export const useApp = () => useContext(AppContext);

export function AppProvider({ children }) {
  const docs = useDocuments();
  const [dark, setDark] = useState(() => localStorage.getItem("theme") === "dark");
  const [health, setHealth] = useState(null);
  const [backendDown, setBackendDown] = useState(false);

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("theme", dark ? "dark" : "light");
  }, [dark]);

  useEffect(() => {
    api.health().then((h) => { setHealth(h); setBackendDown(false); }).catch(() => setBackendDown(true));
  }, []);

  return (
    <AppContext.Provider value={{ ...docs, dark, setDark, health, backendDown }}>{children}</AppContext.Provider>
  );
}
