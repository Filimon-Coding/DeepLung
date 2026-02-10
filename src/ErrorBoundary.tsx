import React from "react";
import type { ReactNode } from "react";

/**
 * Props for ErrorBoundary.
 * children representerer komponentene som "pakkes inn"
 * og beskyttes av ErrorBoundary.
 */
interface ErrorBoundaryProps {
  children: ReactNode;
}

/**
 * State for ErrorBoundary.
 * hasError brukes til å avgjøre om en feil har oppstått.
 */
interface ErrorBoundaryState {
  hasError: boolean;
}

/**
 * ErrorBoundary er en React class component
 * som fanger JavaScript-feil i child-komponenter
 * under rendering, lifecycle-metoder og constructors.
 */
export default class ErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  /**
   * Konstruktør som initialiserer state.
   */
  constructor(props: ErrorBoundaryProps) {
    super(props);

    // Initial state: ingen feil har oppstått
    this.state = { hasError: false };
  }

  /**
   * Denne metoden trigges når en feil oppstår i en child-komponent.
   * Den oppdaterer state slik at fallback-UI vises.
   */
  static getDerivedStateFromError(_error: Error): ErrorBoundaryState {
    return { hasError: true };
  }

  /**
   * componentDidCatch brukes til logging av feilen.
   * Her kan man f.eks. sende feilen til en backend eller
   * et overvåkingsverktøy.
   */
  componentDidCatch(
    error: Error,
    errorInfo: React.ErrorInfo
  ): void {
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
  }

  /**
   * Render-metoden avgjør hva som vises i UI.
   * Hvis en feil har oppstått, vises en feilmelding.
   * Ellers rendres children-komponentene normalt.
   */
  render(): ReactNode {
    if (this.state.hasError) {
      // Fallback UI dersom noe går galt
      return <h2>Noe gikk galt.</h2>;
    }

    // Renderer child-komponentene hvis ingen feil
    return this.props.children;
  }
}