import { Navigate, Outlet } from "react-router-dom";
import { isAuthenticated, mustChangePassword } from "../api/client";

/**
 * Wraps routes that require a valid JWT.
 * Unauthenticated users are redirected to /login.
 */
export default function ProtectedRoute() {
  if (!isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  if (mustChangePassword()) {
    return <Navigate to="/change-password" replace />;
  }

  return <Outlet />;
}
