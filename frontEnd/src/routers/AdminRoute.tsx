import { Navigate, Outlet } from "react-router-dom";

/**
 * Wraps routes that require admin role.
 * Non-admins are redirected to /login.
 */
export default function AdminRoute() {
  const role = localStorage.getItem("role");
  const token = localStorage.getItem("token");

  if (!token) return <Navigate to="/login" replace />;
  if (role !== "admin") return <Navigate to="/analyze" replace />;

  return <Outlet />;
}
