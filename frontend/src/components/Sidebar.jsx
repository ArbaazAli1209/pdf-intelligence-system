import { NavLink } from "react-router-dom";
import { FileText, LayoutDashboard, MessageSquare, Moon, Sun } from "lucide-react";
import { useApp } from "../context/AppContext.jsx";

const links = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard },
  { to: "/documents", label: "Documents", icon: FileText },
  { to: "/chat", label: "Chat", icon: MessageSquare },
];

export default function Sidebar() {
  const { dark, setDark, health } = useApp();
  return (
    <aside className="flex items-center gap-2 border-b border-slate-200 bg-white p-3 dark:border-slate-700 dark:bg-slate-800 md:w-60 md:flex-col md:items-stretch md:border-b-0 md:border-r md:p-4">
      <div className="mr-4 text-lg font-bold text-indigo-600 md:mb-6 md:mr-0">PDF Assistant</div>
      <nav className="flex flex-1 gap-1 md:flex-col">
        {links.map(({ to, label, icon: Icon }) => (
          <NavLink key={to} to={to} end={to === "/"}
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-lg px-3 py-2 text-sm ${isActive ? "bg-indigo-50 font-medium text-indigo-700 dark:bg-slate-700 dark:text-indigo-300" : "hover:bg-slate-100 dark:hover:bg-slate-700"}`}>
            <Icon size={18} /> {label}
          </NavLink>
        ))}
      </nav>
      {health && (
        <div className="hidden rounded-lg bg-slate-100 p-2 text-xs dark:bg-slate-700 md:block">
          Answer mode: <b>{health.answer_mode}</b>
        </div>
      )}
      <button className="btn-ghost" onClick={() => setDark(!dark)} aria-label="Toggle theme">
        {dark ? <Sun size={16} /> : <Moon size={16} />}<span className="hidden md:inline">{dark ? "Light" : "Dark"}</span>
      </button>
    </aside>
  );
}
