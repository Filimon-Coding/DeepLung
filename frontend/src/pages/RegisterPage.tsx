import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";

/**
 * RegisterPage (mock)
 * - Simulerer registrering
 * - Navigerer videre til Analyze etter registrering
 */
function RegisterPage() {
  const navigate = useNavigate();

  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password || !confirmPassword) return;

    if (password !== confirmPassword) {
      alert("Passwords do not match");
      return;
    }

    // Mock register → naviger til Analyze
    navigate("/analyze");
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">
          Create an account to access the AI medical imaging demo.
        </p>

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
              placeholder="Create a password"
            />
          </label>

          <label>
            Confirm Password
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat password"
            />
          </label>

          <button className="auth-button" type="submit">
            Register
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?{" "}
          <Link className="auth-link" to="/login">
            Login
          </Link>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;