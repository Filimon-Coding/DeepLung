import { API_BASE_URL, authHeaders } from "./client";
import type { AnalyzeResponse } from "./analyze";

export type HistoryItem = {
  id: number;
  filename: string;
  prediction: string;
  confidence: number;
  probBenign: number;
  probMalignancy: number;
  createdAtUtc: string;
  hasNifti: boolean;
};

export type HistoryResponse = {
  items: HistoryItem[];
  total: number;
  page: number;
  pageSize: number;
};

export async function fetchHistory(
  page = 1,
  pageSize = 20
): Promise<HistoryResponse> {
  const res = await fetch(
    `${API_BASE_URL}/api/history?page=${page}&pageSize=${pageSize}`,
    { headers: authHeaders() }
  );

  if (!res.ok) {
    if (res.status === 401) throw new Error("Please log in to view history.");
    throw new Error(`Failed to load history (${res.status})`);
  }

  return res.json();
}

export async function fetchHistoryDetail(id: number): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE_URL}/api/history/${id}`, {
    headers: authHeaders(),
  });

  if (!res.ok) throw new Error(`Failed to load result (${res.status})`);

  const d = await res.json();

  return {
    analysis_id:       d.id              ?? d.Id              ?? 0,
    filename:          d.filename        ?? d.Filename        ?? "",
    content_type:      d.contentType     ?? d.content_type    ?? "",
    size_bytes:        d.sizeBytes       ?? d.size_bytes      ?? 0,
    prediction:        d.prediction      ?? d.Prediction      ?? "",
    confidence:        d.confidence      ?? d.Confidence      ?? 0,
    prob_benign:       d.probBenign      ?? d.prob_benign     ?? 0,
    prob_malignancy:   d.probMalignancy  ?? d.prob_malignancy ?? 0,
    slice_base64:      d.sliceBase64     ?? d.slice_base64    ?? null,
    heatmap_base64:    d.heatmapBase64   ?? d.heatmap_base64  ?? null,
    gradcam_nifti_b64: d.gradcamNiftiB64 ?? d.gradcam_nifti_b64 ?? null,
    has_nifti:         d.hasNifti        ?? d.has_nifti        ?? false,
    slice_index:       d.sliceIndex      ?? d.slice_index,
    slice_total:       d.sliceTotal      ?? d.slice_total,
    cam_peak_x:        d.camPeakX        ?? d.cam_peak_x,
    cam_peak_y:        d.camPeakY        ?? d.cam_peak_y,
    cam_peak_z:        d.camPeakZ        ?? d.cam_peak_z,
  };
}

/** Fetch the stored NIfTI file and return it as a File object ready for NiiVue. */
export async function fetchNiftiAsFile(id: number, filename: string): Promise<File> {
  const res = await fetch(`${API_BASE_URL}/api/history/${id}/nifti`, {
    headers: authHeaders(),
  });

  if (!res.ok) throw new Error(`Failed to fetch NIfTI file (${res.status})`);

  const blob = await res.blob();
  return new File([blob], filename, { type: "application/gzip" });
}

export async function deleteHistoryItem(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/history/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  if (!res.ok && res.status !== 204)
    throw new Error(`Failed to delete record (${res.status})`);
}
