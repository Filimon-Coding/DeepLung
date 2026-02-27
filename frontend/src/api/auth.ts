export async function loginUser(email: string, password: string) {
  const res = await fetch("http://127.0.0.1:8000/api/login", { 
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