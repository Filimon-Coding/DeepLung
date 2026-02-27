import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import "./Auth.css";

type Role = "doctor" | "admin";

/**
 * RegisterPage (demo UI)
 * - Allows selecting a role (doctor/admin)
 * - Collects email + password
 * - Demo only: does not persist users yet (no database)
 */
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

  /**
   * Demo register handler
   * - Validates fields
   * - Shows message
   * - Navigates to /login
   */
  const handleRegister = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setSuccessMsg(null);

    // Basic input validation
    if (!email.trim() || !password.trim() || !confirmPassword.trim()) {
      setErrorMsg("Please fill in email and password fields.");
      return;
    }

    if (password !== confirmPassword) {
      setErrorMsg("Passwords do not match.");
      return;
    }

    // Demo-only: no persistence yet
    setSuccessMsg(
      `Demo mode: registration is not persisted. Selected role: ${role}. Use "admin"/"doctor" with password "test123".`
    );

    // Navigate to login after a short delay (so user sees the message)
    setTimeout(() => navigate("/login"), 1000);
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Create Account</h1>
        <p className="auth-subtitle">
          Create an account to access the AI medical imaging demo.
        </p>

        <form className="auth-form" onSubmit={handleRegister}>
          {/* Email */}
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

          {/* Password */}
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

          {/* Confirm Password */}
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

          {/* Role select */}
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

          {/* Feedback */}
          {errorMsg && <p className="auth-error">{errorMsg}</p>}
          {successMsg && <p className="auth-success">{successMsg}</p>}

          {/* Submit */}
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