import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";

/**
 * LoginPage (mock)
 * - Ingen AuthContext / backend ennå
 * - Navigerer bare videre til /analyze når feltene ikke er tomme
 */
function LoginPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) return;

    // Mock login: bare gå videre
    navigate("/analyze");
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Login</h1>
        <p className="auth-subtitle">Sign in to access Analyze and Results.</p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label>
            Email
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@domain.com"
            />
          </label>

          <label>
            Password
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
            />
          </label>

          <button className="auth-button" type="submit">
            Sign in
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