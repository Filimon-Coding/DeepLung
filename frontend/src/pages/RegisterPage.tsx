import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";
import { registerUser } from "../api/auth";

type Role = "doctor" | "admin";

function RegisterPage() {
  const navigate = useNavigate();

  // Form state
  const [role, setRole] = useState<Role>("doctor");
  const [email, setEmail] = useState<string>("");
  const [password, setPassword] = useState<string>("");
  const [confirmPassword, setConfirmPassword] = useState<string>("");

  // UI state
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    if (!email.trim() || !password.trim() || !confirmPassword.trim()) {
      setErrorMsg("Please fill in email and password fields.");
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg("Passwords do not match.");
      return;
    }

    try {
      await registerUser(email, password, confirmPassword, role);
      setSuccessMsg("User created! Redirecting to login...");
      setTimeout(() => navigate("/login"), 800);
    } catch (err) {
      console.error("Register error:", err);
      setErrorMsg(err instanceof Error ? err.message : "Register failed.");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">
          Create an account to access the AI medical imaging demo.
        </p>

        <form className="auth-form" onSubmit={handleRegister}>
          <label className="auth-label">
            Email
            <input
              className="auth-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="name@domain.com"
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
              placeholder="Create a password"
              autoComplete="new-password"
            />
          </label>

          <label className="auth-label">
            Confirm Password
            <input
              className="auth-input"
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Repeat password"
              autoComplete="new-password"
            />
          </label>

          <label className="auth-label">
            Role
            <select
              className="auth-select"
              value={role}
              onChange={(e) => setRole(e.target.value as Role)}
            >
              <option value="doctor">Doctor</option>
              <option value="admin">Admin</option>
            </select>
          </label>

          {errorMsg && <p className="auth-error">{errorMsg}</p>}
          {successMsg && <p className="auth-success">{successMsg}</p>}

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