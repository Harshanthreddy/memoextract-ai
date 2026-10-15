export const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8000";

export async function checkBackendHealth() {
  try {
    const res = await fetch(`${BACKEND_URL}/health`, { cache: "no-store" });
    if (!res.ok) throw new Error("Backend offline");
    return await res.json();
  } catch (err) {
    return { status: "offline", error: err.message };
  }
}

export async function fetchStats() {
  try {
    const res = await fetch(`${BACKEND_URL}/stats`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch stats");
    return await res.json();
  } catch (err) {
    return {
      total_docs: 0,
      successful_docs: 0,
      success_rate: 0,
      needs_review: 0,
      review_rate: 0,
      avg_time_sec: 0,
    };
  }
}

export async function fetchHistory(limit = 50) {
  try {
    const res = await fetch(`${BACKEND_URL}/history?limit=${limit}`, { cache: "no-store" });
    if (!res.ok) throw new Error("Failed to fetch history");
    return await res.json();
  } catch (err) {
    console.error("fetchHistory error:", err);
    return [];
  }
}

export async function deleteHistoryItem(id) {
  try {
    const res = await fetch(`${BACKEND_URL}/history/${id}`, { method: "DELETE" });
    return await res.json();
  } catch (err) {
    return { success: false, error: err.message };
  }
}

export async function extractMarksheet(file, apiKey = "", model = "llama-3.2-11b-vision-preview") {
  const formData = new FormData();
  formData.append("file", file);
  if (apiKey) formData.append("api_key", apiKey);
  if (model) formData.append("model", model);

  const res = await fetch(`${BACKEND_URL}/extract`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || "Extraction failed");
  }

  return await res.json();
}
