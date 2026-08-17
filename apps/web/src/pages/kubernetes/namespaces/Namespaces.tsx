import { useEffect, useState } from "react";
import {
  ArrowLeft,
  CircleAlert,
  Layers3,
  RefreshCw,
  Search,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getNamespaces,
  type Namespace,
} from "../../../api/kubernetes";

import "./Namespaces.css";

function Namespaces() {
  const navigate = useNavigate();

  const { clusterId } = useParams<{
    clusterId: string;
  }>();

  const [namespaces, setNamespaces] = useState<Namespace[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  async function loadNamespaces() {
    if (!clusterId) {
      setError("No Kubernetes cluster selected.");
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError("");

      const data = await getNamespaces(clusterId);

      setNamespaces(data);
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Failed to load Kubernetes namespaces."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadNamespaces();
  }, [clusterId]);

  const filteredNamespaces = namespaces.filter(
    (namespace) =>
      namespace.name
        .toLowerCase()
        .includes(search.toLowerCase())
  );

  return (
    <div className="namespaces-page">
      <div className="namespaces-header">
        <div>
          <button
            className="back-button"
            onClick={() =>
              navigate(
                clusterId
                  ? `/kubernetes/${clusterId}`
                  : "/kubernetes"
              )
            }
          >
            <ArrowLeft size={16} />
            Kubernetes
          </button>

          <p className="eyebrow">
            KUBERNETES OPERATIONS
          </p>

          <h1>Namespaces</h1>

          <p className="subtitle">
            Kubernetes namespaces in the selected cluster
          </p>
        </div>

        <button
          className="refresh-button"
          onClick={loadNamespaces}
          disabled={loading || !clusterId}
        >
          <RefreshCw
            size={16}
            className={loading ? "spin" : ""}
          />
          Refresh
        </button>
      </div>

      {!clusterId && (
        <div className="namespace-state error-state">
          <CircleAlert size={22} />

          <span>
            No cluster selected.
          </span>

          <button
            onClick={() => navigate("/kubernetes")}
          >
            Select Cluster
          </button>
        </div>
      )}

      {clusterId && (
        <>
          <div className="namespace-summary">
            <div className="namespace-summary-card">
              <Layers3 size={19} />

              <div>
                <span>Total Namespaces</span>

                <strong>
                  {loading
                    ? "—"
                    : namespaces.length}
                </strong>
              </div>
            </div>

            <div className="namespace-summary-card">
              <Layers3 size={19} />

              <div>
                <span>Displayed</span>

                <strong>
                  {loading
                    ? "—"
                    : filteredNamespaces.length}
                </strong>
              </div>
            </div>
          </div>

          <section className="namespaces-panel">
            <div className="namespaces-panel-header">
              <div>
                <h2>Kubernetes Namespaces</h2>

                <p>
                  Namespaces available in the selected
                  Kubernetes cluster
                </p>
              </div>

              <Layers3 size={19} />
            </div>

            <div className="namespace-toolbar">
              <div className="namespace-search">
                <Search size={16} />

                <input
                  type="text"
                  placeholder="Search namespaces..."
                  value={search}
                  onChange={(event) =>
                    setSearch(event.target.value)
                  }
                />
              </div>
            </div>

            {loading && (
              <div className="namespace-state">
                <RefreshCw
                  size={22}
                  className="spin"
                />

                <span>
                  Loading namespaces...
                </span>
              </div>
            )}

            {!loading && error && (
              <div className="namespace-state error-state">
                <CircleAlert size={22} />

                <span>{error}</span>

                <button onClick={loadNamespaces}>
                  Try again
                </button>
              </div>
            )}

            {!loading &&
              !error &&
              filteredNamespaces.length === 0 && (
                <div className="namespace-state">
                  <Layers3 size={22} />

                  <span>
                    {search
                      ? "No namespaces match your search."
                      : "No Kubernetes namespaces found."}
                  </span>
                </div>
              )}

            {!loading &&
              !error &&
              filteredNamespaces.length > 0 && (
                <div className="namespaces-table-wrapper">
                  <table className="namespaces-table">
                    <thead>
                      <tr>
                        <th>Namespace</th>
                      </tr>
                    </thead>

                    <tbody>
                      {filteredNamespaces.map(
                        (namespace) => (
                          <tr key={namespace.name}>
                            <td>
                              <div className="namespace-name">
                                <Layers3 size={17} />

                                <strong>
                                  {namespace.name}
                                </strong>
                              </div>
                            </td>
                          </tr>
                        )
                      )}
                    </tbody>
                  </table>
                </div>
              )}
          </section>
        </>
      )}
    </div>
  );
}

export default Namespaces;