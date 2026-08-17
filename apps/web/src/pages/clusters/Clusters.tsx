import { useEffect } from "react";
import {
  CheckCircle2,
  CircleAlert,
  ExternalLink,
  Plus,
  RefreshCw,
  Server,
} from "lucide-react";
import { useNavigate } from "react-router-dom";

import { useCluster } from "../../context/ClusterContext";

import "./Clusters.css";

function Clusters() {
  const navigate = useNavigate();

  const {
    clusters,
    selectedClusterId,
    loading,
    error,
    selectCluster,
    refreshClusters,
  } = useCluster();

  useEffect(() => {
    if (!selectedClusterId && clusters.length > 0) {
      selectCluster(clusters[0].id);
    }
  }, [clusters, selectedClusterId, selectCluster]);

  function openCluster(clusterId: string) {
    selectCluster(clusterId);
    navigate("/kubernetes");
  }

  return (
    <div className="clusters-page">
      <div className="clusters-header">
        <div>
          <p className="eyebrow">INFRASTRUCTURE MANAGEMENT</p>

          <h1>Kubernetes Clusters</h1>

          <p className="subtitle">
            Manage Kubernetes clusters connected to Aegis
          </p>
        </div>

        <div className="clusters-actions">
          <button
            className="refresh-button"
            onClick={refreshClusters}
            disabled={loading}
          >
            <RefreshCw
              size={16}
              className={loading ? "spin" : ""}
            />
            Refresh
          </button>

          <button
            className="add-cluster-button"
            onClick={() => navigate("/clusters/add")}
          >
            <Plus size={17} />
            Add Cluster
          </button>
        </div>
      </div>

      {error && (
        <div className="clusters-error">
          <CircleAlert size={19} />

          <div>
            <strong>Unable to load clusters</strong>
            <span>{error}</span>
          </div>
        </div>
      )}

      {loading && (
        <div className="clusters-state">
          <RefreshCw size={22} className="spin" />
          <span>Loading clusters...</span>
        </div>
      )}

      {!loading && !error && clusters.length === 0 && (
        <div className="clusters-empty">
          <div className="empty-icon">
            <Server size={28} />
          </div>

          <h2>No clusters connected</h2>

          <p>
            Connect your first Kubernetes cluster by uploading
            its kubeconfig file.
          </p>

          <button
            className="add-cluster-button"
            onClick={() => navigate("/clusters/add")}
          >
            <Plus size={17} />
            Attach Cluster
          </button>
        </div>
      )}

      {!loading && !error && clusters.length > 0 && (
        <div className="cluster-grid">
          {clusters.map((cluster) => {
            const online =
              cluster.status.toLowerCase() === "online";

            const selected =
              cluster.id === selectedClusterId;

            return (
              <div
                key={cluster.id}
                className={`cluster-card ${
                  selected ? "selected" : ""
                }`}
              >
                <div className="cluster-card-top">
                  <div className="cluster-icon">
                    <Server size={21} />
                  </div>

                  <span
                    className={`cluster-status ${
                      online ? "online" : "offline"
                    }`}
                  >
                    {online ? (
                      <CheckCircle2 size={14} />
                    ) : (
                      <CircleAlert size={14} />
                    )}

                    {cluster.status}
                  </span>
                </div>

                <div className="cluster-card-content">
                  <h2>{cluster.name}</h2>

                  <span className="cluster-provider">
                    {cluster.provider}
                  </span>

                  <p>
                    {cluster.description ||
                      "No description provided."}
                  </p>
                </div>

                <div className="cluster-card-footer">
                  <span>
                    {selected
                      ? "Currently selected"
                      : "Available cluster"}
                  </span>

                  <button
                    onClick={() => openCluster(cluster.id)}
                  >
                    Open
                    <ExternalLink size={15} />
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Clusters;