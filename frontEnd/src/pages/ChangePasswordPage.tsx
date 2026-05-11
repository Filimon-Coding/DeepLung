import { useState } from "react";
import { Navigate, useNavigate } from "react-router-dom";
import { API_BASE_URL, isAuthenticated } from "../api/client";

async function changePassword(
  currentPassword: string,
  newPassword: string,
  confirmNewPassword: string
): Promise<void> {
  const token = localStorage.getItem("token");
  const res = await fetch(`${API_BASE_URL}/api/change-password`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ currentPassword, newPassword, confirmNewPassword }),
  });

  if (!res.ok) {
    let msg = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      msg = data?.detail || msg;
    } catch {
      /* ignore */
    }
    throw new Error(msg);
  }
}

function ChangePasswordPage() {
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmNewPassword, setConfirmNewPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();
  const isForcedChange =
    localStorage.getItem("mustChangePassword") === "true";
  const role = localStorage.getItem("role");

  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault();
    setErrorMsg(null);

    if (!currentPassword || !newPassword || !confirmNewPassword) {
      setErrorMsg("Please fill in all fields.");
      return;
    }

    if (newPassword !== confirmNewPassword) {
      setErrorMsg("New passwords do not match.");
      return;
    }

    if (newPassword.length < 8) {
      setErrorMsg("New password must be at least 8 characters.");
      return;
    }

    try {
      setLoading(true);
      await changePassword(currentPassword, newPassword, confirmNewPassword);
      localStorage.setItem("mustChangePassword", "false");
      navigate(role === "admin" ? "/admin" : "/analyze");
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to change password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Change password</h1>
        <p className="auth-subtitle">
          {isForcedChange
            ? "You must set a new password before continuing."
            : "Update your account password."}
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-label">
            Current password
            <input
              className="auth-input"
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </label>

          <label className="auth-label">
            New password
            <input
              className="auth-input"
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Min. 8 characters"
              autoComplete="new-password"
            />
          </label>

          <label className="auth-label">
            Confirm new password
            <input
              className="auth-input"
              type="password"
              value={confirmNewPassword}
              onChange={(e) => setConfirmNewPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="new-password"
            />
          </label>

          {errorMsg && <p className="auth-error">{errorMsg}</p>}

          <button className="auth-button" type="submit" disabled={loading}>
            {loading ? "Saving..." : "Save new password"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default ChangePasswordPage;
