import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import {
  getClusters,
  type Cluster,
} from "../api/clusters";

interface ClusterContextValue {
  clusters: Cluster[];
  selectedCluster: Cluster | null;
  selectedClusterId: string | null;

  loading: boolean;
  error: string;

  selectCluster: (clusterId: string) => void;
  refreshClusters: () => Promise<void>;
}

const ClusterContext =
  createContext<ClusterContextValue | undefined>(
    undefined
  );

interface ClusterProviderProps {
  children: ReactNode;
}

export function ClusterProvider({
  children,
}: ClusterProviderProps) {
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [selectedClusterId, setSelectedClusterId] =
    useState<string | null>(
      localStorage.getItem("selectedClusterId")
    );

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  async function refreshClusters() {
    try {
      setLoading(true);
      setError("");

      const response = await getClusters();

      const availableClusters = response.items.filter(
        (cluster) => cluster.is_active
      );

      setClusters(availableClusters);

      /*
       * If the previously selected cluster still exists,
       * keep it selected.
       */
      if (
        selectedClusterId &&
        availableClusters.some(
          (cluster) => cluster.id === selectedClusterId
        )
      ) {
        return;
      }

      /*
       * Otherwise automatically select the first cluster.
       */
      if (availableClusters.length > 0) {
        const firstCluster = availableClusters[0];

        setSelectedClusterId(firstCluster.id);

        localStorage.setItem(
          "selectedClusterId",
          firstCluster.id
        );
      } else {
        setSelectedClusterId(null);
        localStorage.removeItem("selectedClusterId");
      }
    } catch (err) {
      console.error(err);

      setError(
        err instanceof Error
          ? err.message
          : "Failed to load clusters."
      );
    } finally {
      setLoading(false);
    }
  }

  function selectCluster(clusterId: string) {
    const cluster = clusters.find(
      (item) => item.id === clusterId
    );

    if (!cluster) {
      return;
    }

    setSelectedClusterId(cluster.id);

    localStorage.setItem(
      "selectedClusterId",
      cluster.id
    );
  }

  useEffect(() => {
    if (!localStorage.getItem("token")) {
      setClusters([]);
      setSelectedClusterId(null);
      setLoading(false);
      return;
    }

    refreshClusters();
  }, []);

  const selectedCluster = useMemo(() => {
    if (!selectedClusterId) {
      return null;
    }

    return (
      clusters.find(
        (cluster) =>
          cluster.id === selectedClusterId
      ) ?? null
    );
  }, [clusters, selectedClusterId]);

  const value: ClusterContextValue = {
    clusters,
    selectedCluster,
    selectedClusterId,
    loading,
    error,
    selectCluster,
    refreshClusters,
  };

  return (
    <ClusterContext.Provider value={value}>
      {children}
    </ClusterContext.Provider>
  );
}

export function useCluster() {
  const context = useContext(ClusterContext);

  if (!context) {
    throw new Error(
      "useCluster must be used inside ClusterProvider"
    );
  }

  return context;
}