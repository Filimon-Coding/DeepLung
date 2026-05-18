import { createBrowserRouter } from "react-router-dom";
import { lazy } from "react";
import App from "../App";
import ProtectedRoute from "./ProtectedRoute";
import AdminRoute from "./AdminRoute";

const HomePage = lazy(() => import("../pages/HomePage"));
const AnalyzePage = lazy(() => import("../pages/AnalyzePage"));
const ResultsPage = lazy(() => import("../pages/ResultsPage"));
const HistoryPage = lazy(() => import("../pages/HistoryPage"));
const LoginPage = lazy(() => import("../pages/LoginPage"));
const RegisterPage = lazy(() => import("../pages/RegisterPage"));
const ChangePasswordPage = lazy(() => import("../pages/ChangePasswordPage"));
const RequestAccessPage = lazy(() => import("../pages/RequestAccessPage"));
const AdminDashboard = lazy(() => import("../pages/admin/AdminDashboard"));
const AccessRequestsPage = lazy(() => import("../pages/admin/AccessRequestsPage"));
const UsersPage = lazy(() => import("../pages/admin/UsersPage"));
const SystemMonitorPage = lazy(() => import("../pages/admin/SystemMonitorPage"));

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },
      { path: "change-password", element: <ChangePasswordPage /> },
      { path: "request-access", element: <RequestAccessPage /> },

      {
        element: <ProtectedRoute />,
        children: [
          { path: "analyze", element: <AnalyzePage /> },
          { path: "results", element: <ResultsPage /> },
          { path: "history", element: <HistoryPage /> },
        ],
      },

      {
        path: "admin",
        element: <AdminRoute />,
        children: [
          { index: true, element: <AdminDashboard /> },
          { path: "requests", element: <AccessRequestsPage /> },
          { path: "users", element: <UsersPage /> },
          { path: "monitor", element: <SystemMonitorPage /> },
        ],
      },
    ],
  },
]);

export default router;
