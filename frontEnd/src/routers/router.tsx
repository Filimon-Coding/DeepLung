import { createBrowserRouter } from "react-router-dom";
import App from "../App";
import ProtectedRoute from "./ProtectedRoute";
import AdminRoute from "./AdminRoute";

import HomePage from "../pages/HomePage";
import AnalyzePage from "../pages/AnalyzePage";
import ResultsPage from "../pages/ResultsPage";
import HistoryPage from "../pages/HistoryPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";
import ChangePasswordPage from "../pages/ChangePasswordPage";
import RequestAccessPage from "../pages/RequestAccessPage";
import AdminDashboard from "../pages/admin/AdminDashboard";
import AccessRequestsPage from "../pages/admin/AccessRequestsPage";
import UsersPage from "../pages/admin/UsersPage";
import SystemMonitorPage from "../pages/admin/SystemMonitorPage";

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
