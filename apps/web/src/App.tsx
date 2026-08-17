import { BrowserRouter, NavLink, Route, Routes } from "react-router-dom";
import Kubernetes from "./pages/kubernetes/Kubernetes";
import { useState } from "react";
import Login from "./pages/login/Login";
import KubernetesResource from "./pages/kubernetes/resource/KubernetesResource";
import Nodes from "./pages/kubernetes/nodes/Nodes";
import Namespaces from "./pages/kubernetes/namespaces/Namespaces";
import {
  Activity,
  AlertTriangle,
  Bell,
  Boxes,
  BrainCircuit,
  ChevronDown,
  CircleUserRound,
  FileText,
  Gauge,
  GitBranch,
  LayoutDashboard,
  Network,
  Settings,
  ShieldCheck,
  Users,
} from "lucide-react";
import "./App.css";

const navigation = [
  { label: "Dashboard", path: "/", icon: LayoutDashboard },
  { label: "Incidents", path: "/incidents", icon: AlertTriangle },
  { label: "Kubernetes", path: "/kubernetes", icon: Boxes },
  { label: "RCA", path: "/rca", icon: BrainCircuit },
  { label: "Remediation", path: "/remediation", icon: ShieldCheck },
  { label: "Timeline", path: "/timeline", icon: GitBranch },
  { label: "Monitoring", path: "/monitoring", icon: Activity },
  { label: "Alerts", path: "/alerts", icon: Bell },
  { label: "Clusters", path: "/clusters", icon: Network },
  { label: "Reports", path: "/reports", icon: FileText },
  { label: "Users", path: "/users", icon: Users },
  { label: "Settings", path: "/settings", icon: Settings },
];

function PlaceholderPage({ title }: { title: string }) {
  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">AEGIS AI SRE</p>
          <h1>{title}</h1>
        </div>
      </div>

      <div className="empty-state">
        <Gauge size={32} />
        <h2>{title}</h2>
        <p>This module will be connected to the backend next.</p>
      </div>
    </div>
  );
}

function Dashboard() {
  return (
    <div className="page">
      <div className="page-header">
        <div>
          <p className="eyebrow">AEGIS AI SRE</p>
          <h1>Dashboard</h1>
          <p className="subtitle">
            Kubernetes reliability and incident intelligence
          </p>
        </div>

        <button className="cluster-selector">
          <span className="status-dot" />
          Production Cluster
          <ChevronDown size={16} />
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <span>Active Incidents</span>
          <strong>0</strong>
          <small>No active incidents</small>
        </div>

        <div className="stat-card critical">
          <span>Critical Incidents</span>
          <strong>0</strong>
          <small>Requires attention</small>
        </div>

        <div className="stat-card success">
          <span>Auto Remediated</span>
          <strong>0</strong>
          <small>Successfully resolved</small>
        </div>

        <div className="stat-card">
          <span>Cluster Health</span>
          <strong>100%</strong>
          <small>All systems operational</small>
        </div>
      </div>

      <div className="dashboard-grid">
        <section className="panel activity-panel">
          <div className="panel-header">
            <div>
              <h2>Incident Activity</h2>
              <p>Recent reliability events</p>
            </div>
            <Activity size={20} />
          </div>

          <div className="chart-placeholder">
            <Activity size={40} />
            <span>Incident activity will appear here</span>
          </div>
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>System Status</h2>
              <p>Current platform health</p>
            </div>
          </div>

          <div className="status-list">
            <div>
              <span>API</span>
              <strong className="healthy">Healthy</strong>
            </div>
            <div>
              <span>Kubernetes</span>
              <strong className="healthy">Healthy</strong>
            </div>
            <div>
              <span>Prometheus</span>
              <strong className="healthy">Healthy</strong>
            </div>
            <div>
              <span>Remediation Engine</span>
              <strong className="healthy">Ready</strong>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}

function App() {
  const [authenticated, setAuthenticated] = useState(
    () => Boolean(localStorage.getItem("token"))
  );

  if (!authenticated) {
    return (
      <Login
        onLogin={() => {
          setAuthenticated(true);
        }}
      />
    );
  }

  return (
    <BrowserRouter>
      <div className="app-shell">
        <aside className="sidebar">
          <div className="brand">
            <div className="brand-mark">
              <ShieldCheck size={22} />
            </div>
            <div>
              <strong>AEGIS</strong>
              <span>AI SRE PLATFORM</span>
            </div>
          </div>

          <nav>
            <p className="nav-section">PLATFORM</p>

            {navigation.map(({ label, path, icon: Icon }) => (
              <NavLink
                key={path}
                to={path}
                className={({ isActive }) =>
                  `nav-item ${isActive ? "active" : ""}`
                }
              >
                <Icon size={18} />
                <span>{label}</span>
              </NavLink>
            ))}
          </nav>

          <div className="sidebar-footer">
            <div className="online-indicator" />
            <span>Platform Online</span>
          </div>
        </aside>

        <main className="main">
          <header className="topbar">
            <div className="breadcrumb">
              <span>Aegis</span>
              <span>/</span>
              <strong>Operations</strong>
            </div>

            <div className="topbar-actions">
              <button className="icon-button">
                <Bell size={19} />
              </button>

              <div className="user">
                <CircleUserRound size={28} />
                <div>
                  <strong>Operator</strong>
                  <span>SRE Admin</span>
                </div>
              </div>
            </div>
          </header>

          <Routes>
            <Route path="/" element={<Dashboard />} />

            <Route
              path="/kubernetes"
              element={<Kubernetes />}
            />

              <Route
              path="/kubernetes/:clusterId"
              element={<Kubernetes />}
            />

            <Route
              path="/kubernetes/:clusterId/nodes"
              element={<Nodes />}
            />
            <Route
              path="/kubernetes/:clusterId/namespaces"
              element={<Namespaces />}
            />
            <Route
              path="/kubernetes/:clusterId/:resource"
              element={<KubernetesResource />}
            />
            {navigation
              .filter((item) => item.path !== "/")
              .map((item) => (
                <Route
                  key={item.path}
                  path={item.path}
                  element={<PlaceholderPage title={item.label} />}
                />
              ))}
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
