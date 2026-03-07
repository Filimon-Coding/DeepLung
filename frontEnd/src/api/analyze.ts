import { API_BASE_URL, authHeaders } from "./client";

export type AnalyzeResponse = {
  filename: string;
  content_type: string;
  size_bytes: number;
  prediction: string;
  confidence: number;
  prob_benign: number;
  prob_malignancy: number;
  slice_base64: string | null;
  heatmap_base64: string | null;
};

async function readError(res: Response): Promise<string> {
  try {
    const data = await res.json();
    return data?.detail || data?.message || `Request failed (${res.status})`;
  } catch {
    try {
      const text = await res.text();
      return text || `Request failed (${res.status})`;
    } catch {
      return `Request failed (${res.status})`;
    }
  }
}

export async function analyzeImage(file: File): Promise<AnalyzeResponse> {
  const formData = new FormData();

  // Most ASP.NET Core endpoints bind this fine with "file".
  // If your backend action uses [FromForm] IFormFile File, binder is case-insensitive.
  formData.append("file", file);

  const res = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: "POST",
    headers: authHeaders(),
    body: formData,
  });

  if (!res.ok) {
    throw new Error(await readError(res));
  }

  return res.json();
}