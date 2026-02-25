import React, { createContext, useContext, useMemo, useState } from "react";

export type Prediction = {
  predictedClass: "Cancer" | "No cancer" | "Unknown";
  confidence: number; // 0..100
  createdAtISO: string;
};

type AnalysisState = {
  file: File | null;
  uploadedPreviewUrl: string | null;
  heatmapUrl: string | null;
  prediction: Prediction | null;

  setFile: (f: File | null) => void;
  runMockAnalysis: () => void;
  reset: () => void;
};

const AnalysisContext = createContext<AnalysisState | null>(null);

export function AnalysisProvider({ children }: { children: React.ReactNode }) {
  const [file, setFileInternal] = useState<File | null>(null);
  const [uploadedPreviewUrl, setUploadedPreviewUrl] = useState<string | null>(null);
  const [heatmapUrl, setHeatmapUrl] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);

  const setFile = (f: File | null) => {
    if (uploadedPreviewUrl) URL.revokeObjectURL(uploadedPreviewUrl);

    setFileInternal(f);
    setPrediction(null);

    if (!f) {
      setUploadedPreviewUrl(null);
      setHeatmapUrl(null);
      return;
    }

    setUploadedPreviewUrl(URL.createObjectURL(f));
    setHeatmapUrl("/heatmap-placeholder.png");
  };

  const runMockAnalysis = () => {
    const isCancer = Math.random() > 0.5;
    const conf = Math.round(70 + Math.random() * 28);

    setPrediction({
      predictedClass: isCancer ? "Cancer" : "No cancer",
      confidence: conf,
      createdAtISO: new Date().toISOString(),
    });
  };

  const reset = () => {
    if (uploadedPreviewUrl) URL.revokeObjectURL(uploadedPreviewUrl);
    setFileInternal(null);
    setUploadedPreviewUrl(null);
    setHeatmapUrl(null);
    setPrediction(null);
  };

  const value = useMemo(
    () => ({
      file,
      uploadedPreviewUrl,
      heatmapUrl,
      prediction,
      setFile,
      runMockAnalysis,
      reset,
    }),
    [file, uploadedPreviewUrl, heatmapUrl, prediction]
  );

  return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>;
}

export function useAnalysis() {
  const ctx = useContext(AnalysisContext);
  if (!ctx) throw new Error("useAnalysis must be used within AnalysisProvider");
  return ctx;
}