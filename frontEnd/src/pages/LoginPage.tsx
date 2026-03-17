import { useState } from "react";
import { Navigate, useNavigate, Link } from "react-router-dom";
import { loginUser } from "../api/auth";
import { isAuthenticated } from "../api/client";

function LoginPage() {
  const [userId, setUserId] = useState("");
  const [password, setPassword] = useState("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const navigate = useNavigate();

  if (isAuthenticated()) {
    const role = localStorage.getItem("role");
    return <Navigate to={role === "admin" ? "/admin" : "/analyze"} replace />;
  }

  async function handleSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    setErrorMsg(null);

    if (!userId.trim() || !password.trim()) {
      setErrorMsg("Please enter your user ID and password.");
      return;
    }

    try {
      setLoading(true);
      const data = await loginUser(userId.trim(), password);
      if (data.mustChangePassword) {
        navigate("/change-password");
      } else if (data.role === "admin") {
        navigate("/admin");
      } else {
        navigate("/analyze");
      }
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Sign in</h1>
        <p className="auth-subtitle">Access Analyze and your scan history.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-label">
            User ID
            <input
              className="auth-input"
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              placeholder="yobe2801"
              autoComplete="username"
            />
          </label>

          <label className="auth-label">
            Password
            <input
              className="auth-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </label>

          {errorMsg && <p className="auth-error">{errorMsg}</p>}

          <button className="auth-button" type="submit" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="auth-footer">
          New employee?{" "}
          <Link to="/request-access" className="auth-link">
            Request access
          </Link>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;