const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
  params?: Record<string, string>
): Promise<T> {
  const url = new URL(`${API_BASE_URL}${path}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.set(key, value);
    });
  }

  const token = localStorage.getItem("token");

  const response = await fetch(url.toString(), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(token
        ? {
            Authorization: `Bearer ${token}`,
          }
        : {}),
      ...(options.headers || {}),
    },
  });

  if (!response.ok) {
    const errorText = await response.text();

    throw new Error(
      errorText || `API request failed: ${response.status}`
    );
  }

  return response.json();
}

export function apiGet<T>(
  path: string,
  params?: Record<string, string>
): Promise<T> {
  return apiRequest<T>(
    path,
    {
      method: "GET",
    },
    params
  );
}

export function apiPost<T>(
  path: string,
  body?: unknown,
  params?: Record<string, string>
): Promise<T> {
  return apiRequest<T>(
    path,
    {
      method: "POST",
      body:
        body !== undefined
          ? JSON.stringify(body)
          : undefined,
    },
    params
  );
}