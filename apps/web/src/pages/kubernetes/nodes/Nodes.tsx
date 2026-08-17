import { useEffect, useState } from "react";
import {
  ArrowLeft,
  CheckCircle2,
  CircleAlert,
  RefreshCw,
  Server,
} from "lucide-react";
import { useNavigate, useParams } from "react-router-dom";

import { apiGet } from "../../../api/client";
import "./Nodes.css";

interface NodeData {
  name: string;
  status: string;
  roles: string;
  kubelet_version: string;
  os: string;
  architecture: string;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
}

function Nodes() {
  const navigate = useNavigate();

  /*
   * Cluster ID comes from the URL.
   *
   * IMPORTANT:
   * There is NO hardcoded cluster ID here.
   *
   * Example URL:
   * /kubernetes/01KZG5FQW9KDF7ASGHSNWN0CK2/nodes
   */
  const { clusterId } = useParams<{
    clusterId: string;
  }>();

  const [nodes, setNodes] = useState<NodeData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function loadNodes() {
    /*
     * Do not call the API without a selected cluster.
     */
    if (!clusterId) {
      setNodes([]);
      setError(
        "No Kubernetes cluster selected. Please select a cluster first."
      );
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");

    try {
      /*
       * apiGet() automatically adds:
       *
       * Authorization: Bearer <token>
       *
       * The cluster ID is dynamically taken from the URL.
       */
      const response = await apiGet<ApiResponse<NodeData[]>>(
        "/kubernetes/nodes",
        {
          cluster_id: clusterId,
        }
      );

      if (!response.success) {
        throw new Error("Failed to load Kubernetes nodes.");
      }

      setNodes(response.data);
    } catch (err) {
      console.error("Failed to load Kubernetes nodes:", err);

      setNodes([]);

      setError(
        err instanceof Error
          ? err.message
          : "Failed to load Kubernetes nodes."
      );
    } finally {
      setLoading(false);
    }
  }

  /*
   * Load nodes whenever the selected cluster changes.
   */
  useEffect(() => {
    loadNodes();
  }, [clusterId]);

  /*
   * Calculate node health.
   */
  const readyNodes = nodes.filter(
    (node) => node.status.toLowerCase() === "ready"
  );

  const notReadyNodes = nodes.filter(
    (node) => node.status.toLowerCase() !== "ready"
  );

  return (
    <div className="nodes-page">
      {/* =====================================================
          HEADER
          ===================================================== */}

      <div className="nodes-header">
        <div>
          <button
            type="button"
            className="back-button"
            onClick={() => navigate("/kubernetes")}
          >
            <ArrowLeft size={16} />
            Kubernetes
          </button>

          <p className="eyebrow">
            KUBERNETES OPERATIONS
          </p>

          <h1>Nodes</h1>

          <p className="subtitle">
            Cluster nodes and node health
          </p>
        </div>

        <button
          type="button"
          className="refresh-button"
          onClick={loadNodes}
          disabled={loading || !clusterId}
        >
          <RefreshCw
            size={16}
            className={loading ? "spin" : ""}
          />

          {loading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {/* =====================================================
          NO CLUSTER SELECTED
          ===================================================== */}

      {!clusterId && (
        <div className="nodes-state error-state">
          <CircleAlert size={22} />

          <div>
            <strong>No cluster selected</strong>

            <span>
              Please select an attached Kubernetes cluster
              before viewing its nodes.
            </span>
          </div>

          <button
            type="button"
            onClick={() => navigate("/kubernetes")}
          >
            Select Cluster
          </button>
        </div>
      )}

      {/* =====================================================
          CLUSTER SELECTED
          ===================================================== */}

      {clusterId && (
        <>
          {/* =================================================
              NODE SUMMARY
              ================================================= */}

          <div className="nodes-summary">
            <div className="node-summary-card">
              <Server size={19} />

              <div>
                <span>Total Nodes</span>

                <strong>
                  {loading ? "—" : nodes.length}
                </strong>
              </div>
            </div>

            <div className="node-summary-card">
              <CheckCircle2 size={19} />

              <div>
                <span>Ready</span>

                <strong>
                  {loading ? "—" : readyNodes.length}
                </strong>
              </div>
            </div>

            <div className="node-summary-card">
              <CircleAlert size={19} />

              <div>
                <span>Not Ready</span>

                <strong>
                  {loading ? "—" : notReadyNodes.length}
                </strong>
              </div>
            </div>
          </div>

          {/* =================================================
              NODES PANEL
              ================================================= */}

          <section className="nodes-panel">
            <div className="nodes-panel-header">
              <div>
                <h2>Cluster Nodes</h2>

                <p>
                  Kubernetes nodes connected to the selected
                  cluster
                </p>
              </div>

              <Server size={19} />
            </div>

            {/* =================================================
                LOADING
                ================================================= */}

            {loading && (
              <div className="nodes-state">
                <RefreshCw
                  size={22}
                  className="spin"
                />

                <span>
                  Loading Kubernetes nodes...
                </span>
              </div>
            )}

            {/* =================================================
                ERROR
                ================================================= */}

            {!loading && error && (
              <div className="nodes-state error-state">
                <CircleAlert size={22} />

                <div>
                  <strong>
                    Unable to load nodes
                  </strong>

                  <span>{error}</span>
                </div>

                <button
                  type="button"
                  onClick={loadNodes}
                >
                  Try Again
                </button>
              </div>
            )}

            {/* =================================================
                EMPTY
                ================================================= */}

            {!loading &&
              !error &&
              nodes.length === 0 && (
                <div className="nodes-state">
                  <Server size={22} />

                  <span>
                    No Kubernetes nodes found in this
                    cluster.
                  </span>
                </div>
              )}

            {/* =================================================
                NODE TABLE
                ================================================= */}

            {!loading &&
              !error &&
              nodes.length > 0 && (
                <div className="nodes-table-wrapper">
                  <table className="nodes-table">
                    <thead>
                      <tr>
                        <th>Node</th>
                        <th>Status</th>
                        <th>Role</th>
                        <th>Kubernetes</th>
                        <th>OS</th>
                        <th>Architecture</th>
                      </tr>
                    </thead>

                    <tbody>
                      {nodes.map((node) => {
                        const ready =
                          node.status.toLowerCase() ===
                          "ready";

                        return (
                          <tr key={node.name}>
                            {/* Node name */}

                            <td>
                              <div className="node-name">
                                <Server size={17} />

                                <strong>
                                  {node.name}
                                </strong>
                              </div>
                            </td>

                            {/* Status */}

                            <td>
                              <span
                                className={`node-status ${
                                  ready
                                    ? "ready"
                                    : "not-ready"
                                }`}
                              >
                                {ready ? (
                                  <CheckCircle2
                                    size={14}
                                  />
                                ) : (
                                  <CircleAlert
                                    size={14}
                                  />
                                )}

                                {node.status ||
                                  "Unknown"}
                              </span>
                            </td>

                            {/* Role */}

                            <td>
                              <span className="role-badge">
                                {node.roles || "—"}
                              </span>
                            </td>

                            {/* Kubernetes version */}

                            <td>
                              {node.kubelet_version ||
                                "—"}
                            </td>

                            {/* Operating system */}

                            <td>
                              {node.os || "—"}
                            </td>

                            {/* Architecture */}

                            <td>
                              {node.architecture ||
                                "—"}
                            </td>
                          </tr>
                        );
                      })}
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

export default Nodes;