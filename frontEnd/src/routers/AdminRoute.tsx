import { Navigate, Outlet } from "react-router-dom";
import { mustChangePassword } from "../api/client";

/**
 * Wraps routes that require admin role.
 * Non-admins are redirected to /login.
 */
export default function AdminRoute() {
  const role = localStorage.getItem("role");
  const token = localStorage.getItem("token");

  if (!token) return <Navigate to="/login" replace />;
  if (mustChangePassword()) return <Navigate to="/change-password" replace />;
  if (role !== "admin") return <Navigate to="/analyze" replace />;

  return <Outlet />;
}
