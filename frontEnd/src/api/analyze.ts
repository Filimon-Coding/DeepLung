import { API_BASE_URL } from "./client";

export type AnalyzeResponse = {
  filename: string;
  content_type: string;
  size_bytes: number;
  prediction: string;
  confidence: number;
};

/**
 * Uploads an image file to the backend and returns the analysis response.
 */
export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();
  formData.append("File", file);

  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const msg = await res.text();
    throw new Error(msg || `Request failed with status ${res.status}`);
  }

  return res.json();
}