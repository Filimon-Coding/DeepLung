import { API_BASE_URL, authHeaders } from "./client";

export type AnalyzeResponse = {
  analysis_id: number;
  filename: string;
  content_type: string;
  size_bytes: number;
  prediction: string;
  confidence: number;
  prob_benign: number;
  prob_malignancy: number;
  slice_base64: string | null;
  heatmap_base64: string | null;
  gradcam_nifti_b64: string | null;
  has_nifti?: boolean;
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

  const d = await res.json();
  return {
    analysis_id:       d.analysisId      ?? d.analysis_id      ?? 0,
    filename:          d.filename        ?? d.Filename          ?? "",
    content_type:      d.contentType     ?? d.content_type      ?? "",
    size_bytes:        d.sizeBytes       ?? d.size_bytes        ?? 0,
    prediction:        d.prediction      ?? d.Prediction        ?? "",
    confidence:        d.confidence      ?? d.Confidence        ?? 0,
    prob_benign:       d.probBenign      ?? d.prob_benign       ?? 0,
    prob_malignancy:   d.probMalignancy  ?? d.prob_malignancy   ?? 0,
    slice_base64:      d.middleSliceB64  ?? d.slice_base64      ?? null,
    heatmap_base64:    d.gradcamB64      ?? d.heatmap_base64    ?? null,
    gradcam_nifti_b64: d.gradcamNiftiB64 ?? d.gradcam_nifti_b64 ?? null,
    has_nifti:         true,
  };
}