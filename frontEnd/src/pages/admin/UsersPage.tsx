import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  getAdminUsers,
  updateAdminUser,
  deleteAdminUser,
  resetUserPassword,
  type AdminUser,
} from "../../api/admin";
import { generateTempPassword } from "../../utils/userId";

const POSITIONS = ["Doctor", "Nurse", "Radiologist", "Radiographer", "Surgeon", "Other"];
const ROLES = ["doctor", "admin"];

type EditModal = { user: AdminUser; mode: "edit" | "reset-pw" | "delete" };

function DetailCell({ label, value }: { label: string; value: string | null }) {
  return (
    <div className="admin-detail-item">
      <span className="admin-detail-label">{label}</span>
      <span className="admin-detail-value">{value || "—"}</span>
    </div>
  );
}

function fmt(iso: string) {
  return new Date(iso).toLocaleDateString("no-NO", {
    day: "2-digit", month: "2-digit", year: "numeric",
  });
}

function UsersPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [modal, setModal] = useState<EditModal | null>(null);

  // Edit form state
  const [editFirstName, setEditFirstName] = useState("");
  const [editLastName, setEditLastName] = useState("");
  const [editEmail, setEditEmail] = useState("");
  const [editMobile, setEditMobile] = useState("");
  const [editPosition, setEditPosition] = useState("");
  const [editRole, setEditRole] = useState("");

  // Reset password state
  const [newPassword, setNewPassword] = useState("");

  const [saving, setSaving] = useState(false);
  const [modalError, setModalError] = useState<string | null>(null);

  useEffect(() => { load(); }, []);

  async function load() {
    try {
      setLoading(true);
      setErrorMsg(null);
      setUsers(await getAdminUsers());
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Failed to load users.");
    } finally {
      setLoading(false);
    }
  }

  function openEdit(user: AdminUser) {
    setEditFirstName(user.firstName ?? "");
    setEditLastName(user.lastName ?? "");
    setEditEmail(user.email);
    setEditMobile(user.mobileNumber ?? "");
    setEditPosition(user.position ?? POSITIONS[0]);
    setEditRole(user.role);
    setModalError(null);
    setModal({ user, mode: "edit" });
  }

  function openResetPw(user: AdminUser) {
    setNewPassword(generateTempPassword());
    setModalError(null);
    setModal({ user, mode: "reset-pw" });
  }

  function openDelete(user: AdminUser) {
    setModalError(null);
    setModal({ user, mode: "delete" });
  }

  async function saveEdit() {
    if (!modal) return;
    try {
      setSaving(true);
      setModalError(null);
      const updated = await updateAdminUser(modal.user.id, {
        firstName: editFirstName,
        lastName: editLastName,
        email: editEmail,
        mobileNumber: editMobile,
        position: editPosition,
        role: editRole,
      });
      setUsers(prev => prev.map(u => u.id === updated.id ? { ...u, ...updated } : u));
      setModal(null);
    } catch (err) {
      setModalError(err instanceof Error ? err.message : "Update failed.");
    } finally {
      setSaving(false);
    }
  }

  async function saveResetPw() {
    if (!modal) return;
    try {
      setSaving(true);
      setModalError(null);
      await resetUserPassword(modal.user.id, newPassword);
      setModal(null);
    } catch (err) {
      setModalError(err instanceof Error ? err.message : "Reset failed.");
    } finally {
      setSaving(false);
    }
  }

  async function confirmDelete() {
    if (!modal) return;
    try {
      setSaving(true);
      setModalError(null);
      await deleteAdminUser(modal.user.id);
      setUsers(prev => prev.filter(u => u.id !== modal.user.id));
      setModal(null);
    } catch (err) {
      setModalError(err instanceof Error ? err.message : "Delete failed.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="admin-page">
      <p style={{ fontFamily: "var(--font-mono)", fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.5rem" }}>
        <Link to="/admin" style={{ color: "var(--primary)" }}>Dashboard</Link>{" / "}Users
      </p>

      <h1 className="admin-page-title">Users</h1>
      <p className="admin-page-sub">
        Manage staff accounts — edit details, reset passwords, or remove access.
      </p>

      {loading && (
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", color: "var(--text-muted)" }}>
          <span className="nifti-spinner" /> Loading…
        </div>
      )}
      {errorMsg && <p className="auth-error">{errorMsg}</p>}

      {!loading && !errorMsg && users.length === 0 && (
        <div style={{ textAlign: "center", padding: "3.5rem 1rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", color: "var(--text-muted)" }}>
          <p style={{ fontSize: "2rem", marginBottom: "0.75rem" }}>👤</p>
          <p>No user accounts yet.</p>
        </div>
      )}

      {users.length > 0 && (
        <section className="admin-section">
          <div className="admin-section-header">
            <h2 className="admin-section-title">All accounts</h2>
            <span className="admin-count-badge">{users.length}</span>
          </div>

          {users.map(user => (
            <div key={user.id} className="admin-request-card-expanded">
              {/* Top row */}
              <div className="admin-request-card-top">
                <span className="admin-request-card-name">
                  {user.firstName ?? ""} {user.lastName ?? ""}
                  {!user.firstName && !user.lastName && (
                    <span style={{ color: "var(--text-muted)" }}>—</span>
                  )}
                  <span className={`admin-badge admin-badge--${user.role === "admin" ? "pending" : "approved"}`}>
                    {user.role}
                  </span>
                  {user.mustChangePassword && (
                    <span className="admin-badge admin-badge--rejected" title="Must change password on next login">
                      pw reset
                    </span>
                  )}
                </span>
                <div className="admin-request-actions">
                  <button className="admin-btn admin-btn-approve" onClick={() => openEdit(user)}>
                    Edit
                  </button>
                  <button
                    className="admin-btn admin-btn-reject"
                    style={{ borderColor: "var(--warning)", color: "var(--warning)" }}
                    onClick={() => openResetPw(user)}
                  >
                    Reset pw
                  </button>
                  <button className="admin-btn admin-btn-reject" onClick={() => openDelete(user)}>
                    Delete
                  </button>
                </div>
              </div>

              {/* Detail grid */}
              <div className="admin-detail-grid">
                <DetailCell label="User ID"    value={user.userId} />
                <DetailCell label="First name" value={user.firstName} />
                <DetailCell label="Last name"  value={user.lastName} />
                <DetailCell label="Email"      value={user.email} />
                <DetailCell label="Mobile"     value={user.mobileNumber} />
                <DetailCell label="Position"   value={user.position} />
                <DetailCell label="Created"    value={fmt(user.createdAt)} />
              </div>
            </div>
          ))}
        </section>
      )}

      {/* ── Modals ── */}
      {modal && (
        <div className="modal-overlay" onClick={() => !saving && setModal(null)}>
          <div className="modal-card" onClick={e => e.stopPropagation()}>

            {/* Edit */}
            {modal.mode === "edit" && (
              <>
                <h2 className="modal-title">Edit user</h2>
                <p className="modal-subtitle">
                  Updating details for{" "}
                  <strong style={{ color: "#fff" }}>{modal.user.userId}</strong>
                </p>
                <div className="modal-form">
                  <div className="modal-two-col">
                    <label className="modal-label">
                      First name
                      <input className="modal-input" value={editFirstName}
                        onChange={e => setEditFirstName(e.target.value)} />
                    </label>
                    <label className="modal-label">
                      Last name
                      <input className="modal-input" value={editLastName}
                        onChange={e => setEditLastName(e.target.value)} />
                    </label>
                  </div>
                  <label className="modal-label">
                    Email
                    <input className="modal-input" type="email" value={editEmail}
                      onChange={e => setEditEmail(e.target.value)} />
                  </label>
                  <label className="modal-label">
                    Mobile
                    <input className="modal-input" type="tel" value={editMobile}
                      onChange={e => setEditMobile(e.target.value)} />
                  </label>
                  <div className="modal-two-col">
                    <label className="modal-label">
                      Position
                      <select className="modal-select" value={editPosition}
                        onChange={e => setEditPosition(e.target.value)}>
                        {POSITIONS.map(p => <option key={p} value={p}>{p}</option>)}
                      </select>
                    </label>
                    <label className="modal-label">
                      Role
                      <select className="modal-select" value={editRole}
                        onChange={e => setEditRole(e.target.value)}>
                        {ROLES.map(r => <option key={r} value={r}>{r}</option>)}
                      </select>
                    </label>
                  </div>
                </div>

                {modalError && <p className="auth-error" style={{ marginTop: "1rem" }}>{modalError}</p>}

                <div className="modal-actions" style={{ marginTop: "1.5rem" }}>
                  <button className="admin-btn admin-btn-reject" onClick={() => setModal(null)} disabled={saving}>
                    Cancel
                  </button>
                  <button className="admin-btn admin-btn-approve" onClick={saveEdit} disabled={saving}>
                    {saving ? "Saving…" : "Save changes"}
                  </button>
                </div>
              </>
            )}

            {/* Reset password */}
            {modal.mode === "reset-pw" && (
              <>
                <h2 className="modal-title">Reset password</h2>
                <p className="modal-subtitle">
                  A new temporary password will be set for{" "}
                  <strong style={{ color: "#fff" }}>{modal.user.userId}</strong>.
                  {" "}The user must change it on next login.
                </p>
                <div className="modal-field">
                  <label className="modal-label">New temporary password</label>
                  <div className="modal-copy-row">
                    <input
                      className="modal-input"
                      style={{ fontFamily: "var(--font-mono)", color: "var(--primary)" }}
                      value={newPassword}
                      onChange={e => setNewPassword(e.target.value)}
                    />
                    <button className="modal-copy-btn" onClick={() => {
                      navigator.clipboard.writeText(newPassword);
                    }}>
                      Copy
                    </button>
                  </div>
                </div>

                {modalError && <p className="auth-error" style={{ marginBottom: "1rem" }}>{modalError}</p>}

                <div className="modal-actions">
                  <button className="admin-btn admin-btn-reject" onClick={() => setModal(null)} disabled={saving}>
                    Cancel
                  </button>
                  <button className="admin-btn admin-btn-approve" onClick={saveResetPw} disabled={saving}>
                    {saving ? "Resetting…" : "Set new password"}
                  </button>
                </div>
              </>
            )}

            {/* Delete */}
            {modal.mode === "delete" && (
              <>
                <h2 className="modal-title" style={{ color: "var(--danger)" }}>Remove user</h2>
                <p className="modal-subtitle">
                  This will permanently delete the account for{" "}
                  <strong style={{ color: "#fff" }}>
                    {modal.user.firstName ?? ""} {modal.user.lastName ?? ""} ({modal.user.userId})
                  </strong>
                  {" "}and all their analysis history. This cannot be undone.
                </p>

                <div className="confirm-delete-strip">
                  <p>Are you sure you want to remove this account?</p>
                  <button className="admin-btn-danger" onClick={confirmDelete} disabled={saving}>
                    {saving ? "Deleting…" : "Yes, delete"}
                  </button>
                </div>

                {modalError && <p className="auth-error" style={{ marginTop: "1rem" }}>{modalError}</p>}

                <div className="modal-actions" style={{ marginTop: "1rem" }}>
                  <button className="admin-btn admin-btn-reject" onClick={() => setModal(null)} disabled={saving}>
                    Cancel
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default UsersPage;
