import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./index.css";

/**
 * Henter root-elementet fra index.html.
 * Dette er elementet React-applikasjonen rendres inn i.
 */
const rootElement = document.getElementById("root");

/**
 * Sikkerhetssjekk:
 * TypeScript tillater at getElementById kan returnere null.
 * Hvis root-elementet ikke finnes, stopper vi applikasjonen
 * med en tydelig feilmelding.
 */
if (!rootElement) {
  throw new Error("Root element not found");
}

/**
 * Oppretter React sin root (React 18).
 * StrictMode brukes for å fange potensielle problemer
 * under utvikling (kun i dev, ikke i production).
 */
createRoot(rootElement).render(
  <StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </StrictMode>
);