import { apiGet } from "./client";

export interface Cluster {
  id: string;
  name: string;
  description: string | null;
  provider: string;
  status: string;
  is_active: boolean;
}

interface ClusterListData {
  items: Cluster[];
  total: number;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
}

export async function getClusters(): Promise<ClusterListData> {
  const response = await apiGet<ApiResponse<ClusterListData>>(
    "/clusters"
  );

  return response.data;
}

export async function getCluster(
  clusterId: string
): Promise<Cluster> {
  const response = await apiGet<ApiResponse<Cluster>>(
    `/clusters/${clusterId}`
  );

  return response.data;
}