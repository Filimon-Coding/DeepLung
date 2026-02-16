import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar/Navbar";
import HomePage from "./pages/HomePage";
import AnalyzePage from "./pages/AnalyzePage";
import ResultsPage from "./pages/ResultsPage";
import "./App.css";

function App() {
  return (
    <>
    <Navbar />
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/analyze" element={<AnalyzePage />} />
      <Route path="/results" element={<ResultsPage />} />
    </Routes>
    </>
  );
}

export default App;