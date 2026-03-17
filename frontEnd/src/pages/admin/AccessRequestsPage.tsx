import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getAccessRequests,
  approveRequest,
  rejectRequest,
  type AccessRequest,
} from "../../api/admin";
import { generateUserId, generateTempPassword } from "../../utils/userId";

type ApproveModal = {
  request: AccessRequest;
  userId: string;
  tempPassword: string;
};

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString("no-NO", {
    day: "2-digit", month: "2-digit", year: "numeric",
  });
}

function DetailRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="admin-detail-item">
      <span className="admin-detail-label">{label}</span>
      <span className="admin-detail-value">{value}</span>
    </div>
  );
}

function AccessRequestsPage() {
  const [requests, setRequests] = useState<AccessRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [modal, setModal] = useState<ApproveModal | null>(null);
  const [approving, setApproving] = useState(false);
  const [approveError, setApproveError] = useState<string | null>(null);
  const [confirmed, setConfirmed] = useState(false);
  const [copiedField, setCopiedField] = useState<"id" | "pw" | null>(null);
  // Cache generated credentials per request so reopening the modal shows the same password
  const credCache = useState<Map<number, { userId: string; tempPassword: string }>>(new Map)[0];

  useEffect(() => { loadRequests(); }, []);

  async function loadRequests() {
    try {
      setLoading(true);
      setErrorMsg(null);
      setRequests(await getAccessRequests());
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to load requests.");
    } finally {
      setLoading(false);
    }
  }

  function openApproveModal(req: AccessRequest) {
    let creds = credCache.get(req.id);
    if (!creds) {
      creds = {
        userId: generateUserId(req.firstName, req.lastName, req.personnummer, []),
        tempPassword: generateTempPassword(),
      };
      credCache.set(req.id, creds);
    }
    setModal({ request: req, ...creds });
    setApproveError(null);
    setConfirmed(false);
  }

  async function confirmApprove() {
    if (!modal) return;
    try {
      setApproving(true);
      setApproveError(null);
      await approveRequest(modal.request.id, modal.userId, modal.tempPassword);
      setConfirmed(true);
      setRequests(prev =>
        prev.map(r => r.id === modal.request.id ? { ...r, status: "approved" } : r)
      );
    } catch (err) {
      setApproveError(err instanceof Error ? err.message : "Approval failed.");
    } finally {
      setApproving(false);
    }
  }

  async function handleReject(id: number) {
    if (!confirm("Reject this access request?")) return;
    try {
      await rejectRequest(id);
      setRequests(prev => prev.map(r => r.id === id ? { ...r, status: "rejected" } : r));
    } catch (err) {
      alert(err instanceof Error ? err.message : "Rejection failed.");
    }
  }

  function copy(text: string, field: "id" | "pw") {
    navigator.clipboard.writeText(text);
    setCopiedField(field);
    setTimeout(() => setCopiedField(null), 2000);
  }

  const pending = requests.filter(r => r.status === "pending");
  const handled = requests.filter(r => r.status !== "pending");

  return (
    <div className="admin-page">

      <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.5rem" }}>
        <Link to="/admin" style={{ color: "var(--primary)" }}>Dashboard</Link>
        {" / "}Access Requests
      </p>

      <h1 className="admin-page-title">Access Requests</h1>
      <p className="admin-page-sub">
        Review pending requests and create accounts for new staff members.
      </p>

      {loading && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", color: "var(--text-muted)" }}>
          <span className="nifti-spinner" /> Loading…
        </div>
      )}
      {errorMsg && <p className="auth-error">{errorMsg}</p>}

      {!loading && !errorMsg && requests.length === 0 && (
        <div style={{ textAlign: "center", padding: "3.5rem 1rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", color: "var(--text-muted)" }}>
          <p style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>📭</p>
          <p>No access requests yet.</p>
        </div>
      )}

      {/* ── Pending ── */}
      {pending.length > 0 && (
        <section className="admin-section">
          <div className="admin-section-header">
            <h2 className="admin-section-title">Pending</h2>
            <span className="admin-count-badge">{pending.length}</span>
          </div>

          {pending.map(req => (
            <div key={req.id} className="admin-request-card-expanded">
              <div className="admin-request-card-top">
                <span className="admin-request-card-name">
                  {req.firstName} {req.lastName}
                  <span className="admin-badge admin-badge--pending">{req.position}</span>
                </span>
                <div className="admin-request-actions">
                  <button className="admin-btn admin-btn-approve" onClick={() => openApproveModal(req)}>
                    Approve
                  </button>
                  <button className="admin-btn admin-btn-reject" onClick={() => handleReject(req.id)}>
                    Reject
                  </button>
                </div>
              </div>

              <div className="admin-detail-grid">
                <DetailRow label="First name"    value={req.firstName} />
                <DetailRow label="Last name"     value={req.lastName} />
                <DetailRow label="Personnummer"  value={req.personnummer} />
                <DetailRow label="Email"         value={req.email} />
                <DetailRow label="Mobile"        value={req.mobileNumber} />
                <DetailRow label="Position"      value={req.position} />
                <DetailRow label="Submitted"     value={fmt(req.submittedAt)} />
              </div>
            </div>
          ))}
        </section>
      )}

      {/* ── Handled ── */}
      {handled.length > 0 && (
        <section className="admin-section">
          <div className="admin-section-header">
            <h2 className="admin-section-title">Handled</h2>
            <span className="admin-count-badge">{handled.length}</span>
          </div>

          {handled.map(req => (
            <div key={req.id} className={`admin-request-card-expanded admin-request-card--${req.status}`}>
              <div className="admin-request-card-top">
                <span className="admin-request-card-name">
                  {req.firstName} {req.lastName}
                </span>
                <span className={`admin-badge admin-badge--${req.status}`}>{req.status}</span>
              </div>
              <div className="admin-detail-grid">
                <DetailRow label="Personnummer" value={req.personnummer} />
                <DetailRow label="Email"        value={req.email} />
                <DetailRow label="Mobile"       value={req.mobileNumber} />
                <DetailRow label="Position"     value={req.position} />
                <DetailRow label="Submitted"    value={fmt(req.submittedAt)} />
              </div>
            </div>
          ))}
        </section>
      )}

      {/* ── Approve modal ── */}
      {modal && (
        <div className="modal-overlay" onClick={() => !approving && !confirmed && setModal(null)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>
            {!confirmed ? (
              <>
                <h2 className="modal-title">Create account</h2>
                <p className="modal-subtitle">
                  Review credentials for{" "}
                  <strong style={{ color: "#fff" }}>{modal.request.firstName} {modal.request.lastName}</strong>.
                  {" "}Copy and send them to the user <em>before</em> confirming.
                </p>

                <div className="modal-field">
                  <label className="modal-label">Generated User ID</label>
                  <div className="modal-copy-row">
                    <code className="modal-value">{modal.userId}</code>
                    <button className="modal-copy-btn" onClick={() => copy(modal.userId, "id")}>
                      {copiedField === "id" ? "✓ Copied" : "Copy"}
                    </button>
                  </div>
                </div>

                <div className="modal-field">
                  <label className="modal-label">Temporary Password</label>
                  <div className="modal-copy-row">
                    <code className="modal-value">{modal.tempPassword}</code>
                    <button className="modal-copy-btn" onClick={() => copy(modal.tempPassword, "pw")}>
                      {copiedField === "pw" ? "✓ Copied" : "Copy"}
                    </button>
                  </div>
                </div>

                <p className="modal-note">
                  The user signs in with their User ID and this temporary password.
                  They will be prompted to set a new password on first login.
                </p>

                {approveError && <p className="auth-error" style={{ marginBottom: "1rem" }}>{approveError}</p>}

                <div className="modal-actions">
                  <button className="admin-btn admin-btn-reject" onClick={() => setModal(null)} disabled={approving}>
                    Cancel
                  </button>
                  <button className="admin-btn admin-btn-approve" onClick={confirmApprove} disabled={approving}>
                    {approving ? "Creating…" : "Confirm & create account"}
                  </button>
                </div>
              </>
            ) : (
              <>
                <h2 className="modal-title" style={{ color: "var(--success)" }}>Account created</h2>
                <p className="modal-subtitle">
                  The account for{" "}
                  <strong style={{ color: "#fff" }}>{modal.request.firstName} {modal.request.lastName}</strong>
                  {" "}has been created successfully.
                </p>
                <div className="modal-field">
                  <label className="modal-label">User ID</label>
                  <code className="modal-value" style={{ display: "block" }}>{modal.userId}</code>
                </div>
                <div className="modal-actions">
                  <button className="admin-btn admin-btn-approve" onClick={() => setModal(null)}>Done</button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default AccessRequestsPage;
