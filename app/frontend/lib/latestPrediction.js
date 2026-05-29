"use client";

const STORAGE_KEY = "latestPredictionResult";

export function loadLatestPrediction() {
  if (typeof window === "undefined") return null;
  try {
    const saved = window.localStorage.getItem(STORAGE_KEY);
    if (!saved) return null;
    const parsed = JSON.parse(saved);
    if (!parsed || typeof parsed !== "object" || !parsed.prediction || !parsed.comparison) {
      return null;
    }
    return parsed;
  } catch {
    return null;
  }
}

export function saveLatestPrediction(result, selectedFighters = {}) {
  if (typeof window === "undefined") return;
  try {
    window.localStorage.setItem(
      STORAGE_KEY,
      JSON.stringify({
        ...result,
        selected_fighters: selectedFighters,
        saved_at: new Date().toISOString(),
      }),
    );
  } catch {
    // Local storage is optional; the current page still renders the prediction.
  }
}
