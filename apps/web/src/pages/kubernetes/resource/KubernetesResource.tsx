import { useEffect, useState } from "react";
import {
  ArrowLeft,
  Box,
  CircleAlert,
  RefreshCw,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import {
  getNamespaces,
  type Namespace,
} from "../../../api/kubernetes";

import "./KubernetesResource.css";

const resourceTitles: Record<string, string> = {
  overview: "Kubernetes Overview",
  nodes: "Nodes",
  namespaces: "Namespaces",
  pods: "Pods",
  deployments: "Deployments",
  replicasets: "ReplicaSets",
  statefulsets: "StatefulSets",
  daemonsets: "DaemonSets",
  services: "Services",
  yaml: "YAML",
  health: "Cluster Health",
};

function KubernetesResource() {
  const navigate = useNavigate();

  const { resource, clusterId } = useParams<{
    resource: string;
    clusterId: string;
  }>();

  const [namespaces, setNamespaces] = useState<Namespace[]>(
    []
  );

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const title =
    resourceTitles[resource ?? ""] ??
    "Kubernetes Resource";

  async function loadNamespaces() {
    if (!clusterId) {
      setError("No Kubernetes cluster selected.");
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
          : "Failed to load namespaces."
      );
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (resource === "namespaces") {
      loadNamespaces();
    }
  }, [resource, clusterId]);

  return (
    <div className="kubernetes-resource-page">

      {/* Header */}
      <div className="resource-page-header">

        <button
          className="back-button"
          onClick={() => navigate("/kubernetes")}
        >
          <ArrowLeft size={17} />
          Kubernetes
        </button>

        {resource === "namespaces" && (
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
        )}

      </div>

      {/* Title */}
      <div className="resource-page-title">

        <div className="resource-page-icon">
          <Box size={22} />
        </div>

        <div>

          <p className="eyebrow">
            KUBERNETES OPERATIONS
          </p>

          <h1>{title}</h1>

          <p>
            Inspect and manage Kubernetes resources
            from Aegis.
          </p>

        </div>

      </div>

      {/* =====================================================
          Namespaces
         ===================================================== */}

      {resource === "namespaces" && (
        <div className="resource-page-panel">

          <div className="resource-page-panel-header">

            <div>
              <h2>Cluster Namespaces</h2>

              <p>
                Kubernetes namespaces in the selected cluster
              </p>
            </div>

            <span className="resource-count">
              {loading
                ? "..."
                : namespaces.length}
            </span>

          </div>

          {/* No cluster */}
          {!clusterId && (
            <div className="resource-page-empty">

              <CircleAlert size={36} />

              <h2>No Cluster Selected</h2>

              <p>
                Select a Kubernetes cluster before
                viewing namespaces.
              </p>

              <button
                onClick={() => navigate("/kubernetes")}
              >
                Select Cluster
              </button>

            </div>
          )}

          {/* Loading */}
          {clusterId && loading && (
            <div className="resource-page-empty">

              <RefreshCw
                size={32}
                className="spin"
              />

              <h2>Loading Namespaces</h2>

              <p>
                Fetching namespaces from the selected
                Kubernetes cluster.
              </p>

            </div>
          )}

          {/* Error */}
          {clusterId && !loading && error && (
            <div className="resource-page-empty">

              <CircleAlert size={36} />

              <h2>Unable to Load Namespaces</h2>

              <p>{error}</p>

              <button onClick={loadNamespaces}>
                Try Again
              </button>

            </div>
          )}

          {/* Empty */}
          {clusterId &&
            !loading &&
            !error &&
            namespaces.length === 0 && (
              <div className="resource-page-empty">

                <Box size={36} />

                <h2>No Namespaces Found</h2>

                <p>
                  The selected Kubernetes cluster
                  returned no namespaces.
                </p>

              </div>
            )}

          {/* Namespace table */}
          {clusterId &&
            !loading &&
            !error &&
            namespaces.length > 0 && (
              <div className="resource-table-wrapper">

                <table className="resource-table">

                  <thead>
                    <tr>
                      <th>Name</th>
                    </tr>
                  </thead>

                  <tbody>
                    {namespaces.map((namespace) => (
                      <tr key={namespace.name}>
                        <td>
                          <strong>
                            {namespace.name}
                          </strong>
                        </td>
                      </tr>
                    ))}
                  </tbody>

                </table>

              </div>
            )}

        </div>
      )}

      {/* =====================================================
          Other resources
         ===================================================== */}

      {resource !== "namespaces" && (
        <div className="resource-page-panel">

          <div className="resource-page-empty">

            <Box size={36} />

            <h2>{title}</h2>

            <p>
              This resource view is ready to be
              connected to the Kubernetes API.
            </p>

            <small>
              Resource: {resource ?? "unknown"}
            </small>

          </div>

        </div>
      )}

    </div>
  );
}

export default KubernetesResource;