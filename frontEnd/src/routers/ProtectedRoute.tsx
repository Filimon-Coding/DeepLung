import { Navigate, Outlet } from "react-router-dom";
import { isAuthenticated } from "../api/client";

/**
 * Wraps routes that require a valid JWT.
 * Unauthenticated users are redirected to /login.
 */
export default function ProtectedRoute() {
  return isAuthenticated() ? <Outlet /> : <Navigate to="/login" replace />;
}