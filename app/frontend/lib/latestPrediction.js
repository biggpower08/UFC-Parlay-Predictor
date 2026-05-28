"use client";

const STORAGE_KEY = "latestPredictionResult";

export function loadLatestPrediction() {
  if (typeof window === "undefined") return null;
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : null;
  } catch {
    return null;
  }
}

export function saveLatestPrediction(result) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        ...result,
        saved_at: new Date().toISOString(),
      }),
    );
  } catch {
    // Local storage is optional; the current page still renders the prediction.
  }
}
