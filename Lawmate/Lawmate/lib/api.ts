/**
 * Central HTTP client for the Lawmate Next.js app.
 *
 * - Base URL from NEXT_PUBLIC_API_URL (see .env.example or deployment env).
 * - Attaches Bearer JWT from localStorage for authenticated routes.
 * - Exposes small helpers used by feature modules under lib/services/.
 */
const BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

type HttpMethod = "GET" | "POST" | "PUT" | "PATCH" | "DELETE";

function getAuthHeaders(): Record<string, string> {
  if (typeof window === "undefined") return {};
  try {
    const token = localStorage.getItem("token");
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  console.log(`🌐 API Request: ${options.method || "GET"} ${url}`);
  console.log(`   BASE_URL: ${BASE_URL}`);
  
  try {
    const res = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...getAuthHeaders(),
        ...(options.headers || {}),
      },
    });

    console.log(`📥 API Response: ${res.status} ${res.statusText} for ${url}`);

    if (!res.ok) {
      const errText = await res.text().catch(() => "");
      console.error(`❌ API Error: ${res.status} ${res.statusText} - ${errText}`);
      throw new Error(
        `Request failed: ${res.status} ${res.statusText} ${errText}`.trim()
      );
    }

    // Some endpoints may return empty bodies (e.g., 204).
    const text = await res.text();
    const data = text ? (JSON.parse(text) as T) : ({} as T);
    console.log(`✅ API Success: Data received for ${url}`, data);
    return data;
  } catch (error) {
    if (error instanceof TypeError) {
      console.error(`❌ Network error calling ${url}. Backend may be down or restarting.`);
      throw new Error(
        "Network error: unable to reach backend. Please ensure API server is running on http://localhost:8000."
      );
    }
    console.error(`❌ API Request Failed for ${url}:`, error);
    throw error;
  }
}

async function requestMultipart<T>(
  path: string,
  formData: FormData,
  method: HttpMethod = "POST"
): Promise<T> {
  const url = `${BASE_URL}${path}`;
  const res = await fetch(url, {
    method,
    body: formData,
    headers: {
      ...getAuthHeaders(),
    },
  });

  if (!res.ok) {
    const errText = await res.text().catch(() => "");
    throw new Error(
      `Request failed: ${res.status} ${res.statusText} ${errText}`.trim()
    );
  }

  return res.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path, { method: "GET" }),
  post: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "POST",
      body: body ? JSON.stringify(body) : undefined,
    }),
  put: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PUT",
      body: body ? JSON.stringify(body) : undefined,
    }),
  patch: <T>(path: string, body?: unknown) =>
    request<T>(path, {
      method: "PATCH",
      body: body ? JSON.stringify(body) : undefined,
    }),
  delete: <T>(path: string) =>
    request<T>(path, {
      method: "DELETE",
    }),
  postMultipart: <T>(path: string, formData: FormData) =>
    requestMultipart<T>(path, formData, "POST"),
};

export { BASE_URL };

