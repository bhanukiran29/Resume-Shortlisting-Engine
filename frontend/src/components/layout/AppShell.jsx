import { Menu, Search, UserCircle } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";
import Sidebar from "./Sidebar";
import { navigationItems } from "../../constants/navigation";

export default function AppShell() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();
  const activeItem =
    navigationItems.find((item) => item.path === location.pathname) ?? navigationItems[0];

  return (
    <div className="app-shell">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <main className="main">
        <header className="topbar">
          <div className="topbar__tabs">
            <NavLink className="topbar__tab active" to={activeItem.path}>
              {activeItem.label}
            </NavLink>
            <NavLink className="topbar__tab" to="/candidates">
              Candidates
            </NavLink>
          </div>
          <button
            aria-label="Open navigation"
            className="icon-button mobile-menu"
            onClick={() => setSidebarOpen(true)}
            type="button"
          >
            <Menu size={20} />
          </button>
          <div className="topbar__actions">
            <label className="search" aria-label="Search candidates">
              <Search />
              <input className="input" placeholder="Search candidates..." type="search" />
            </label>
            <button className="button secondary" type="button">
              Feedback
            </button>
            <button aria-label="Account" className="icon-button" type="button">
              <UserCircle size={22} />
            </button>
          </div>
        </header>
        <div className="content">
          <motion.div
            key={location.pathname}
            animate={{ opacity: 1, y: 0 }}
            className="content__inner"
            initial={{ opacity: 0, y: 8 }}
            transition={{ duration: 0.18 }}
          >
            <Outlet />
          </motion.div>
        </div>
      </main>
      <AnimatePresence>
        {sidebarOpen ? (
          <motion.button
            aria-label="Close navigation overlay"
            animate={{ opacity: 1 }}
            className="sidebar-backdrop"
            exit={{ opacity: 0 }}
            initial={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            style={{
              position: "fixed",
              inset: 0,
              zIndex: 40,
              border: 0,
              background: "rgb(0 0 0 / 55%)",
            }}
            type="button"
          />
        ) : null}
      </AnimatePresence>
    </div>
  );
}
