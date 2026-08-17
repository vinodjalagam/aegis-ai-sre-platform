export interface ClusterSummary {
  cluster_version: string;
  nodes: number;
  namespaces: number;
  pods: number;
  services: number;
  deployments: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
}
