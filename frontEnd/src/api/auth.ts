import { API_BASE_URL } from "./client";

export type AuthResponse = {
  email: string;
  role: string;
  token: string;
};

async function readError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data?.detail || data?.message || `Request failed (${res.status})`;
  } catch {
    try {
      const text = await res.text();
      return text || `Request failed (${res.status})`;
    } catch {
      return `Request failed (${res.status})`;
    }
  }
}

export async function loginUser(
  email: string,
  password: string
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (!res.ok) {
    throw new Error(await readError(res));
  }

  const data = (await res.json()) as AuthResponse;

  localStorage.setItem("token", data.token);
  localStorage.setItem("email", data.email);
  localStorage.setItem("role", data.role);

  return data;
}

export async function registerUser(
  email: string,
  password: string,
  confirmPassword: string,
  role: "doctor" | "admin" = "doctor"
): Promise<AuthResponse> {
  const res = await fetch(`${API_BASE_URL}/api/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      email,
      password,
      confirmPassword,
      confirm_password: confirmPassword,
      role,
    }),
  });

  if (!res.ok) {
    throw new Error(await readError(res));
  }

  const data = (await res.json()) as AuthResponse;

  localStorage.setItem("token", data.token);
  localStorage.setItem("email", data.email);
  localStorage.setItem("role", data.role);

  return data;
}