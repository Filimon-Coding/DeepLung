import { API_BASE_URL } from "./client";

export async function loginUser(email: string, password: string) {
  const res = await fetch(`${API_BASE_URL}/api/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.detail ?? `Login failed (${res.status})`;
    throw new Error(msg);
  }

  return data;
}

export async function registerUser(
  email: string,
  password: string,
  confirmPassword: string,
  role: "doctor" | "admin" = "doctor"
) {
  const res = await fetch(`${API_BASE_URL}/api/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      password,
      confirm_password: confirmPassword,
      role,
    }),
  });

  const data = await res.json().catch(() => null);

  if (!res.ok) {
    const msg = data?.detail ?? `Register failed (${res.status})`;
    throw new Error(msg);
  }

  return data;
}