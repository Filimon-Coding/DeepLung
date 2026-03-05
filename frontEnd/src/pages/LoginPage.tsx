import { useState } from "react";
import { Link } from "react-router-dom";
import { loginUser } from "../api/auth";
import "./Auth.css";

/**
 * LoginPage
 * - Calls FastAPI POST /api/login
 * - Stores returned role/email in localStorage (demo solution)
 */
function LoginPage() {

  // Form state
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  // UI state
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);

    // Basic validation
    if (!email.trim() || !password.trim()) {
      setErrorMsg("Please enter email and password.");
      return;
    }

    try {
      setIsLoading(true);

      // Call backend (expects: { email, role })
      const result = await loginUser(email, password);

      // Store user info temporarily (until you add real auth/JWT)
      localStorage.setItem("email", result.email);
      localStorage.setItem("role", result.role);

      // Force refresh after login so Navbar updates
      window.location.href = "/analyze";

    } catch (err) {
      console.error("Login error:", err);
      setErrorMsg(err instanceof Error ? err.message : "Login failed.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Login</h1>
        <p className="auth-subtitle">Sign in to access Analyze and Results.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-label">
            Email
            <input
              className="auth-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@crai.com"
              autoComplete="email"
            />
          </label>

          <label className="auth-label">
            Password
            <input
              className="auth-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="test123"
              autoComplete="current-password"
            />
          </label>

          {/* Error message from failed login */}
          {errorMsg && <p className="auth-error">{errorMsg}</p>}

          <button className="auth-button" type="submit" disabled={isLoading}>
            {isLoading ? "Signing in..." : "Sign in"}
          </button>
        </form>

        <div className="auth-footer">
          No account?{" "}
          <Link className="auth-link" to="/register">
            Create one
          </Link>
        </div>
      </div>
    </div>
  );
}

export default LoginPage;