let authToken: string | null = null;

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "";
const API_BASE = baseUrl !== "" ? baseUrl.replace(/\/$/, "") : "/api";

const getHeaders = (initHeaders?: HeadersInit) => {
  const headers = new Headers(initHeaders);
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  if (authToken) {
    headers.set("Authorization", `Bearer ${authToken}`);
  }
  return headers;
};

export const initializeToken = () => {
  if (typeof window === "undefined") {
    return;
  }
  const stored = window.localStorage.getItem("library_token");
  authToken = stored ?? null;
};

export const setToken = (token: string | null) => {
  authToken = token;
  if (typeof window === "undefined") {
    return;
  }
  if (token) {
    window.localStorage.setItem("library_token", token);
  } else {
    window.localStorage.removeItem("library_token");
  }
};

export const getToken = () => authToken;

export const request = async <T>(path: string, init: RequestInit = {}) => {
  const headers = getHeaders(init.headers);
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    cache: "no-store"
  });
  if (!response.ok) {
    let message = "Request failed";
    try {
      const payload = await response.json();
      if (payload?.message) {
        message = payload.message;
      }
    } catch {
    }
    throw new Error(message);
  }
  if (response.status === 204) {
    return null as T;
  }
  return response.json() as Promise<T>;
};
