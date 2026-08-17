import { apiGet, apiPost } from "./client";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: string;
  username: string;
  email?: string | null;
  role?: string | null;
}

interface ApiResponse<T> {
  success: boolean;
  data: T;
}

export async function login(
  credentials: LoginRequest
): Promise<TokenResponse> {
  const result = await apiPost<ApiResponse<TokenResponse>>(
    "/auth/login",
    credentials
  );

  if (!result.success || !result.data?.access_token) {
    throw new Error("Authentication failed");
  }

  localStorage.setItem("token", result.data.access_token);

  return result.data;
}

export async function getCurrentUser(): Promise<User> {
  const result = await apiGet<ApiResponse<User>>("/users/me");

  return result.data;
}

export function logout(): void {
  localStorage.removeItem("token");
}