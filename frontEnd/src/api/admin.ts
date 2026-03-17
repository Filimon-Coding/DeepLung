import { API_BASE_URL } from "./client";

export type AccessRequest = {
  id: number;
  firstName: string;
  lastName: string;
  personnummer: string;
  mobileNumber: string;
  email: string;
  position: string;
  status: "pending" | "approved" | "rejected";
  submittedAt: string;
};

export type CreatedUser = {
  userId: string;
  tempPassword: string;
  email: string;
};

export type AdminUser = {
  id: number;
  userId: string;
  firstName: string | null;
  lastName: string | null;
  email: string;
  mobileNumber: string | null;
  position: string | null;
  role: string;
  mustChangePassword: boolean;
  createdAt: string;
};

function authHeaders() {
  const token = localStorage.getItem("token");
  return {
    "Content-Type": "application/json",
    Authorization: `Bearer ${token}`,
  };
}

async function readError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data?.detail || data?.message || `Request failed (${res.status})`;
  } catch {
    return `Request failed (${res.status})`;
  }
}

export async function submitAccessRequest(data: {
  firstName: string;
  lastName: string;
  personnummer: string;
  mobileNumber: string;
  email: string;
  position: string;
}): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/access-requests`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await readError(res));
}

export async function getAccessRequests(): Promise<AccessRequest[]> {
  const res = await fetch(`${API_BASE_URL}/api/access-requests`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function approveRequest(
  id: number,
  userId: string,
  tempPassword: string
): Promise<CreatedUser> {
  const res = await fetch(`${API_BASE_URL}/api/access-requests/${id}/approve`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ userId, tempPassword }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function rejectRequest(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/access-requests/${id}/reject`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res));
}

// ── User CRUD ────────────────────────────────────────────────────────────────

export async function getAdminUsers(): Promise<AdminUser[]> {
  const res = await fetch(`${API_BASE_URL}/api/admin/users`, {
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function updateAdminUser(
  id: number,
  data: Partial<Pick<AdminUser, "firstName" | "lastName" | "email" | "mobileNumber" | "position" | "role">>
): Promise<AdminUser> {
  const res = await fetch(`${API_BASE_URL}/api/admin/users/${id}`, {
    method: "PUT",
    headers: authHeaders(),
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function deleteAdminUser(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/admin/users/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res));
}

export async function resetUserPassword(id: number, newPassword: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/admin/users/${id}/reset-password`, {
    method: "POST",
    headers: authHeaders(),
    body: JSON.stringify({ newPassword }),
  });
  if (!res.ok) throw new Error(await readError(res));
}
