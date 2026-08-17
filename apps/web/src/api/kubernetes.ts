import { apiGet } from "./client";

import type {
  ApiResponse,
  ClusterSummary,
} from "../types/kubernetes";

/* ============================================================
 * Cluster
 * ============================================================ */

export interface Cluster {
  id: string;
  name: string;
  description: string | null;
  provider: string;
  status: string;
  is_active: boolean;
}

export interface ClusterListResponse {
  items: Cluster[];
  total: number;
}

/* ============================================================
 * Namespace
 * ============================================================ */

export interface Namespace {
  name: string;
}

/* ============================================================
 * Cluster APIs
 * ============================================================ */

export async function getClusters(): Promise<ClusterListResponse> {
  const response = await apiGet<ApiResponse<ClusterListResponse>>(
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

/* ============================================================
 * Kubernetes Summary
 * ============================================================ */

export async function getClusterSummary(
  clusterId: string
): Promise<ClusterSummary> {
  const response = await apiGet<ApiResponse<ClusterSummary>>(
    "/kubernetes/summary",
    {
      cluster_id: clusterId,
    }
  );

  return response.data;
}

/* ============================================================
 * Kubernetes Namespaces
 * ============================================================ */

export async function getNamespaces(
  clusterId: string
): Promise<Namespace[]> {
  const response = await apiGet<ApiResponse<Namespace[]>>(
    "/kubernetes/namespaces",
    {
      cluster_id: clusterId,
    }
  );

  return response.data;
}