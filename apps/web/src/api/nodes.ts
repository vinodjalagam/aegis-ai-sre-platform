import { apiGet } from "./client";

export interface Node {
  name: string;
  status?: string;
  role?: string | null;
  version?: string | null;
  internal_ip?: string | null;
  cpu?: string | null;
  memory?: string | null;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
}

export async function getNodes(
  clusterId: string
): Promise<Node[]> {
  const response = await apiGet<ApiResponse<Node[]>>(
    "/kubernetes/nodes",
    {
      cluster_id: clusterId,
    }
  );

  return response.data;
}
