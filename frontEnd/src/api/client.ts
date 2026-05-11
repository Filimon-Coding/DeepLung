export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:5056";

export function authHeaders(): Record<string, string> {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem("token");
}

export function mustChangePassword(): boolean {
  return localStorage.getItem("mustChangePassword") === "true";
}

export function clearAuth(): void {
  localStorage.removeItem("token");
  localStorage.removeItem("userId");
  localStorage.removeItem("email");
  localStorage.removeItem("role");
  localStorage.removeItem("mustChangePassword");
}
