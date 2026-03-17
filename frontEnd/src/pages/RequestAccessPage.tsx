import { useState } from "react";
import { Link } from "react-router-dom";
import { submitAccessRequest } from "../api/admin";

function RequestAccessPage() {
  const [form, setForm] = useState({
    firstName: "",
    lastName: "",
    personnummer: "",
    mobileNumber: "",
    email: "",
    position: "",
  });
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErrorMsg(null);

    const empty = Object.entries(form).find(([, v]) => !v.trim());
    if (empty) {
      setErrorMsg("Please fill in all fields.");
      return;
    }

    try {
      setLoading(true);
      await submitAccessRequest(form);
      setSubmitted(true);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Submission failed.");
    } finally {
      setLoading(false);
    }
  }

  if (submitted) {
    return (
      <div className="auth-page">
        <div className="auth-card">
          <h1 className="auth-title">Request sent</h1>
          <p className="auth-subtitle">
            Your access request has been submitted. An administrator will review
            it and contact you with your login credentials.
          </p>
          <div className="auth-footer">
            <Link to="/login" className="auth-link">
              Back to sign in
            </Link>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <h1 className="auth-title">Request access</h1>
        <p className="auth-subtitle">
          Fill in your details and an administrator will create your account.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="auth-label">
            First name
            <input
              className="auth-input"
              type="text"
              name="firstName"
              value={form.firstName}
              onChange={handleChange}
              placeholder="Ola"
              autoComplete="given-name"
            />
          </label>

          <label className="auth-label">
            Last name
            <input
              className="auth-input"
              type="text"
              name="lastName"
              value={form.lastName}
              onChange={handleChange}
              placeholder="Nordmann"
              autoComplete="family-name"
            />
          </label>

          <label className="auth-label">
            Personnummer
            <input
              className="auth-input"
              type="text"
              name="personnummer"
              value={form.personnummer}
              onChange={handleChange}
              placeholder="DDMMYYXXXXX"
            />
          </label>

          <label className="auth-label">
            Mobile number
            <input
              className="auth-input"
              type="tel"
              name="mobileNumber"
              value={form.mobileNumber}
              onChange={handleChange}
              placeholder="+47 000 00 000"
              autoComplete="tel"
            />
          </label>

          <label className="auth-label">
            Work email
            <input
              className="auth-input"
              type="email"
              name="email"
              value={form.email}
              onChange={handleChange}
              placeholder="ola@hospital.no"
              autoComplete="email"
            />
          </label>

          <label className="auth-label">
            Position / role
            <input
              className="auth-input"
              type="text"
              name="position"
              value={form.position}
              onChange={handleChange}
              placeholder="Radiologist"
            />
          </label>

          {errorMsg && <p className="auth-error">{errorMsg}</p>}

          <button className="auth-button" type="submit" disabled={loading}>
            {loading ? "Submitting..." : "Submit request"}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?{" "}
          <Link to="/login" className="auth-link">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}

export default RequestAccessPage;
