import { createBrowserRouter } from "react-router-dom";
import App from "../App";
import ProtectedRoute from "./ProtectedRoute";

import HomePage from "../pages/HomePage";
import AnalyzePage from "../pages/AnalyzePage";
import ResultsPage from "../pages/ResultsPage";
import HistoryPage from "../pages/HistoryPage";
import LoginPage from "../pages/LoginPage";
import RegisterPage from "../pages/RegisterPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <HomePage /> },
      { path: "login", element: <LoginPage /> },
      { path: "register", element: <RegisterPage /> },

      {
        element: <ProtectedRoute />,
        children: [
          { path: "analyze", element: <AnalyzePage /> },
          { path: "results", element: <ResultsPage /> },
          { path: "history", element: <HistoryPage /> },
        ],
      },
    ],
  },
]);

export default router;