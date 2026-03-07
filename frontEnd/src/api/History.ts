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
    if (res.status === 401) {
      throw new Error("Please log in to view history.");
    }
    throw new Error(`Failed to load history (${res.status})`);
  }

  return res.json();
}

export async function fetchHistoryDetail(id: number): Promise<AnalyzeResponse> {
  const res = await fetch(`${API_BASE_URL}/api/history/${id}`, {
    headers: authHeaders(),
  });

  if (!res.ok) {
    throw new Error(`Failed to load result (${res.status})`);
  }

  const d = await res.json();

  return {
    filename: d.filename ?? d.Filename ?? "",
    content_type: d.content_type ?? d.contentType ?? "",
    size_bytes: d.size_bytes ?? d.sizeBytes ?? 0,
    prediction: d.prediction ?? d.Prediction ?? "",
    confidence: d.confidence ?? d.Confidence ?? 0,
    prob_benign: d.probBenign ?? d.prob_benign ?? 0,
    prob_malignancy: d.probMalignancy ?? d.prob_malignancy ?? 0,
    slice_base64: d.sliceBase64 ?? d.slice_base64 ?? null,
    heatmap_base64: d.heatmapBase64 ?? d.heatmap_base64 ?? null,
  };
}

export async function deleteHistoryItem(id: number): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/history/${id}`, {
    method: "DELETE",
    headers: authHeaders(),
  });

  if (!res.ok && res.status !== 204) {
    throw new Error(`Failed to delete record (${res.status})`);
  }
}