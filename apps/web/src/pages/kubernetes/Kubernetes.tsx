import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import {
  Activity,
  Box,
  Boxes,
  CircleGauge,
  Container,
  Database,
  FileCode2,
  GitBranch,
  Layers3,
  Network,
  Server,
  ShieldCheck,
} from "lucide-react";

import {
  getClusters,
  type Cluster,
} from "../../api/clusters";

import {
  getClusterSummary,
} from "../../api/kubernetes";

import type {
  ClusterSummary,
} from "../../types/kubernetes";

import "./Kubernetes.css";

const resources = [
  {
    label: "Overview",
    icon: CircleGauge,
    description: "Cluster health and resource summary",
  },
  {
    label: "Nodes",
    icon: Server,
    description: "Cluster nodes and node health",
  },
  {
    label: "Namespaces",
    icon: Layers3,
    description: "Kubernetes namespaces",
  },
  {
    label: "Pods",
    icon: Box,
    description: "Running workloads and pod status",
  },
  {
    label: "Deployments",
    icon: Boxes,
    description: "Deployment workloads and replicas",
  },
  {
    label: "ReplicaSets",
    icon: GitBranch,
    description: "ReplicaSet workloads",
  },
  {
    label: "StatefulSets",
    icon: Database,
    description: "Stateful workloads",
  },
  {
    label: "DaemonSets",
    icon: Container,
    description: "Node-level workloads",
  },
  {
    label: "Services",
    icon: Network,
    description: "Kubernetes services and networking",
  },
  {
    label: "YAML",
    icon: FileCode2,
    description: "View, validate, diff and apply YAML",
  },
  {
    label: "Health",
    icon: ShieldCheck,
    description: "Cluster and workload health",
  },
];

function Kubernetes() {
  const navigate = useNavigate();

  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [selectedCluster, setSelectedCluster] =
    useState<Cluster | null>(null);

  const [summary, setSummary] =
    useState<ClusterSummary | null>(null);

  const [loadingClusters, setLoadingClusters] =
    useState(true);

  const [loadingSummary, setLoadingSummary] =
    useState(false);

  const [error, setError] = useState("");

  /*
   * Load clusters belonging to the authenticated user.
   */
  useEffect(() => {
    async function loadClusters() {
      try {
        setLoadingClusters(true);
        setError("");

        const response = await getClusters();

        setClusters(response.items);

        /*
         * Select the first available cluster.
         *
         * No cluster ID is hard-coded.
         */
        if (response.items.length > 0) {
          setSelectedCluster(response.items[0]);
        } else {
          setSelectedCluster(null);
        }
      } catch (err) {
        console.error(err);

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load clusters."
        );
      } finally {
        setLoadingClusters(false);
      }
    }

    loadClusters();
  }, []);

  /*
   * Load Kubernetes summary whenever
   * the selected cluster changes.
   */
  useEffect(() => {
    if (!selectedCluster) {
      setSummary(null);
      return;
    }

    const clusterId = selectedCluster.id;

    async function loadSummary() {
      try {
        setLoadingSummary(true);
        setError("");

        const data = await getClusterSummary(clusterId);

        setSummary(data);
      } catch (err) {
        console.error(err);

        setError(
          err instanceof Error
            ? err.message
            : "Failed to load Kubernetes summary."
        );
      } finally {
        setLoadingSummary(false);
      }
    }

    loadSummary();
  }, [selectedCluster]);

  /*
   * Navigate to a Kubernetes resource.
   *
   * IMPORTANT:
   * The cluster ID always comes from selectedCluster.id.
   * Nothing is hard-coded here.
   */
  function openResource(label: string) {
    if (!selectedCluster) {
      return;
    }

    const clusterId = selectedCluster.id;

    switch (label) {
      case "Nodes":
        navigate(`/kubernetes/${clusterId}/nodes`);
        break;

      default:
        break;
    }
  }

  const loading =
    loadingClusters || loadingSummary;

  return (
    <div className="kubernetes-page">

      {/* ================================
          Header
      ================================= */}

      <div className="kubernetes-header">

        <div>
          <p className="eyebrow">
            KUBERNETES OPERATIONS
          </p>

          <h1>
            Kubernetes
          </h1>

          <p className="subtitle">
            Manage and observe Kubernetes resources from Aegis
          </p>
        </div>

        {/* Cluster selector */}

        <div className="cluster-selector">

          <label htmlFor="cluster-select">
            Cluster
          </label>

          <select
            id="cluster-select"
            value={selectedCluster?.id ?? ""}
            disabled={
              loadingClusters ||
              clusters.length === 0
            }
            onChange={(event) => {
              const cluster = clusters.find(
                (item) =>
                  item.id === event.target.value
              );

              if (cluster) {
                setSelectedCluster(cluster);
              }
            }}
          >

            {clusters.length === 0 && (
              <option value="">
                No clusters available
              </option>
            )}

            {clusters.map((cluster) => (
              <option
                key={cluster.id}
                value={cluster.id}
              >
                {cluster.name}
              </option>
            ))}

          </select>
        </div>
      </div>

      {/* ================================
          Cluster status
      ================================= */}

      {selectedCluster && (
        <div className="cluster-status">

          <span className="status-dot" />

          <div>
            <strong>
              {selectedCluster.name}
            </strong>

            <span>
              {error
                ? "Connection error"
                : loading
                  ? "Connecting..."
                  : selectedCluster.status}
            </span>
          </div>

        </div>
      )}

      {/* ================================
          No cluster
      ================================= */}

      {!loadingClusters &&
        clusters.length === 0 &&
        !error && (
          <div className="kubernetes-error">

            <strong>
              No Kubernetes clusters found
            </strong>

            <span>
              Add a cluster with its kubeconfig to start
              managing Kubernetes.
            </span>

          </div>
        )}

      {/* ================================
          Error
      ================================= */}

      {error && (
        <div className="kubernetes-error">

          <strong>
            Unable to load Kubernetes data
          </strong>

          <span>
            {error}
          </span>

        </div>
      )}

      {/* ================================
          Summary
      ================================= */}

      {selectedCluster && (
        <div className="kubernetes-summary">

          <div className="kube-stat">

            <span>
              Cluster Version
            </span>

            <strong>
              {loading
                ? "..."
                : summary?.cluster_version ?? "—"}
            </strong>

            <small>
              Kubernetes cluster
            </small>

          </div>

          <div className="kube-stat">

            <span>
              Nodes
            </span>

            <strong>
              {loading
                ? "..."
                : summary?.nodes ?? "—"}
            </strong>

            <small>
              Cluster nodes
            </small>

          </div>

          <div className="kube-stat">

            <span>
              Pods
            </span>

            <strong>
              {loading
                ? "..."
                : summary?.pods ?? "—"}
            </strong>

            <small>
              Running workloads
            </small>

          </div>

          <div className="kube-stat">

            <span>
              Deployments
            </span>

            <strong>
              {loading
                ? "..."
                : summary?.deployments ?? "—"}
            </strong>

            <small>
              Application workloads
            </small>

          </div>

          <div className="kube-stat">

            <span>
              Services
            </span>

            <strong>
              {loading
                ? "..."
                : summary?.services ?? "—"}
            </strong>

            <small>
              Kubernetes services
            </small>

          </div>

        </div>
      )}

      {/* ================================
          Resources
      ================================= */}

      {selectedCluster && (
        <div className="resource-section">

          <div className="section-heading">

            <div>

              <h2>
                Kubernetes Resources
              </h2>

              <p>
                Select a resource to manage and inspect it.
              </p>

            </div>

            <Activity size={19} />

          </div>

          <div className="resource-grid">

            {resources.map(
              ({
                label,
                icon: Icon,
                description,
              }) => (
                <button
                  key={label}
                  className="resource-card"
                  onClick={() => {
                    if (!selectedCluster) {
                      return;
                    }

                    if (label === "Nodes") {
                      navigate(
                        `/kubernetes/${selectedCluster.id}/nodes`
                      );
                      return;
                    }

                    const resourcePath = label
                      .toLowerCase()
                      .replace("replicasets", "replicasets")
                      .replace("statefulsets", "statefulsets")
                      .replace("daemonsets", "daemonsets");

                    navigate(
                      `/kubernetes/${selectedCluster.id}/${resourcePath}`
                    );
                  }}
                >

                  <div className="resource-icon">
                    <Icon size={20} />
                  </div>

                  <div className="resource-content">

                    <strong>
                      {label}
                    </strong>

                    <span>
                      {description}
                    </span>

                  </div>

                </button>
              )
            )}

          </div>

        </div>
      )}

    </div>
  );
}

export default Kubernetes;