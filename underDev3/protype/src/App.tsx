import { Routes, Route } from "react-router-dom";

import Index from "./pages/Index";
import Analyze from "./pages/Analyze";
import Results from "./pages/Results";
import Login from "./pages/Login";
import NotFound from "./pages/NotFound";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Index />} />
      <Route path="/analyze" element={<Analyze />} />
      <Route path="/results" element={<Results />} />
      <Route path="/login" element={<Login />} />

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}