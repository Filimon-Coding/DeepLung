import { useState } from "react";
import { Link } from "react-router-dom";
import { submitAccessRequest } from "../api/admin";

const POSITIONS = [
  "Doctor",
  "Nurse",
  "Radiologist",
  "Radiographer",
  "Surgeon",
  "Other",
];

function RegisterPage() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [personnummer, setPersonnummer] = useState("");
  const [mobileNumber, setMobileNumber] = useState("");
  const [email, setEmail] = useState("");
  const [position, setPosition] = useState(POSITIONS[0]);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  function validatePersonnummer(value: string): boolean {
    return /^\d{11}$/.test(value.replace(/\s/g, ""));
  }

  async function handleSubmit(e: { preventDefault(): void }) {
    e.preventDefault();
    setErrorMsg(null);

    if (
      !firstName.trim() ||
      !lastName.trim() ||
      !personnummer.trim() ||
      !mobileNumber.trim() ||
      !email.trim()
    ) {
      setErrorMsg("Please fill in all fields.");
      return;
    }

    if (!validatePersonnummer(personnummer)) {
      setErrorMsg("Personnummer must be exactly 11 digits.");
      return;
    }

    if (!/^\d{8,12}$/.test(mobileNumber.replace(/\s/g, ""))) {
      setErrorMsg("Please enter a valid mobile number.");
      return;
    }

    try {
      setLoading(true);
      await submitAccessRequest({
        firstName: firstName.trim(),
        lastName: lastName.trim(),
        personnummer: personnummer.replace(/\s/g, ""),
        mobileNumber: mobileNumber.replace(/\s/g, ""),
        email: email.trim(),
        position,
      });
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
          <h1 className="auth-title">Request submitted</h1>
          <p className="auth-subtitle">
            Your access request has been sent. The administrator will review it
            and contact you with your login credentials.
          </p>
          <div className="auth-footer">
            <Link className="auth-link" to="/login">
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
          Fill in your details. The admin will create your account and send you
          your login credentials.
        </p>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
            <label className="auth-label">
              First name
              <input
                className="auth-input"
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                placeholder="Tor"
                autoComplete="given-name"
              />
            </label>

            <label className="auth-label">
              Last name
              <input
                className="auth-input"
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                placeholder="Benhaid"
                autoComplete="family-name"
              />
            </label>
          </div>

          <label className="auth-label">
            Personnummer (11 digits)
            <input
              className="auth-input"
              type="text"
              value={personnummer}
              onChange={(e) => setPersonnummer(e.target.value)}
              placeholder="28080312345"
              inputMode="numeric"
              maxLength={11}
            />
          </label>

          <label className="auth-label">
            Mobile number
            <input
              className="auth-input"
              type="tel"
              value={mobileNumber}
              onChange={(e) => setMobileNumber(e.target.value)}
              placeholder="89784536"
              autoComplete="tel"
            />
          </label>

          <label className="auth-label">
            Private email
            <input
              className="auth-input"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="younes.benhaid@gmail.com"
              autoComplete="email"
            />
          </label>

          <label className="auth-label">
            Position / Role
            <select
              className="auth-select"
              value={position}
              onChange={(e) => setPosition(e.target.value)}
            >
              {POSITIONS.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </label>

          {errorMsg && <p className="auth-error">{errorMsg}</p>}

          <button className="auth-button" type="submit" disabled={loading}>
            {loading ? "Submitting..." : "Submit request"}
          </button>
        </form>

        <div className="auth-footer">
          Already have an account?{" "}
          <Link className="auth-link" to="/login">
            Sign in
          </Link>
        </div>
      </div>
    </div>
  );
}

export default RegisterPage;
