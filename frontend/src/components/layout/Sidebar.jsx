import {
  BarChart2,
  Bell,
  FileText,
  HelpCircle,
  LayoutDashboard,
  Plus,
  Settings,
  UploadCloud,
  Users,
  Workflow,
  X,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { navigationItems } from "../../constants/navigation";

const iconMap = {
  dashboard: LayoutDashboard,
  upload: UploadCloud,
  job: FileText,
  candidates: Users,
  processing: Workflow,
  analytics: BarChart2,
  settings: Settings,
};

export default function Sidebar({ open, onClose }) {
  return (
    <aside className={`sidebar ${open ? "open" : ""}`}>
      <div className="sidebar__brand">
        <div className="brand-mark">R</div>
        <div>
          <h1 className="brand-title">RecruitAI</h1>
          <div className="brand-plan">Enterprise Plan</div>
        </div>
        <button
          aria-label="Close navigation"
          className="icon-button mobile-menu"
          onClick={onClose}
          style={{ marginLeft: "auto" }}
          type="button"
        >
          <X size={18} />
        </button>
      </div>
      <nav className="sidebar__section" aria-label="Primary navigation">
        <NavLink className="nav-action primary" to="/upload" onClick={onClose}>
          <Plus size={18} />
          New Upload
        </NavLink>
        {navigationItems.map((item) => {
          const Icon = iconMap[item.icon];
          return (
            <NavLink
              className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
              end={item.path === "/"}
              key={item.path}
              onClick={onClose}
              to={item.path}
            >
              <Icon size={20} />
              {item.label}
            </NavLink>
          );
        })}
      </nav>
      <div className="sidebar__footer">
        <button className="nav-item" type="button">
          <HelpCircle size={20} />
          Support
        </button>
        <button className="nav-item" type="button">
          <Bell size={20} />
          Notifications
        </button>
      </div>
    </aside>
  );
}
