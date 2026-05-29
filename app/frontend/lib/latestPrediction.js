"use client";

import { useEffect, useState } from "react";

export const LATEST_PREDICTION_KEY = "ufc_latest_prediction";
export const LATEST_PREDICTION_EVENT = "ufc_latest_prediction_updated";
const SCHEMA_VERSION = 1;
const LEGACY_STORAGE_KEY = "latestPredictionResult";

function isBrowser() {
  return typeof window !== "undefined";
}

function dispatchLatestPredictionEvent() {
  if (!isBrowser()) return;
  window.dispatchEvent(new Event(LATEST_PREDICTION_EVENT));
}

function normalizeLatestPrediction(raw) {
  if (!raw || typeof raw !== "object") return null;
  if (!raw.prediction || !raw.comparison) return null;

  const statsA = raw.comparison?.stats1 || {};
  const statsB = raw.comparison?.stats2 || {};
  const generatedAt = raw.generatedAt || raw.saved_at || new Date().toISOString();
  const fighterA = raw.fighterA || raw.selectedFighters?.fighter_a || raw.selected_fighters?.fighter_a || statsA;
  const fighterB = raw.fighterB || raw.selectedFighters?.fighter_b || raw.selected_fighters?.fighter_b || statsB;
  const predictionKey =
    raw.predictionKey ||
    raw.prediction_id ||
    `${statsA.Name || fighterA?.name || "fighter-a"}::${statsB.Name || fighterB?.name || "fighter-b"}::${generatedAt}`;

  return {
    ...raw,
    schemaVersion: SCHEMA_VERSION,
    predictionKey,
    generatedAt,
    fighterA,
    fighterB,
    selectedFighters: {
      fighter_a: fighterA,
      fighter_b: fighterB,
    },
    analysis: raw.analysis || {},
    propReads: raw.propReads || raw.analysis?.prop_reads || [],
    confidence: raw.confidence ?? raw.prediction?.confidence ?? null,
    volatility: raw.volatility ?? raw.analysis?.volatility_label ?? null,
    dataQuality: raw.dataQuality ?? raw.analysis?.data_quality_label ?? null,
    matchupType: raw.matchupType ?? raw.analysis?.matchup_type ?? null,
  };
}

export function loadLatestPrediction() {
  if (!isBrowser()) return null;
  try {
    const saved = window.localStorage.getItem(LATEST_PREDICTION_KEY);
    window.localStorage.removeItem(LEGACY_STORAGE_KEY);
    if (!saved) return null;
    const parsed = JSON.parse(saved);
    const normalized = normalizeLatestPrediction(parsed);
    if (!normalized) {
      window.localStorage.removeItem(LATEST_PREDICTION_KEY);
      return null;
    }
    return normalized;
  } catch {
    window.localStorage.removeItem(LATEST_PREDICTION_KEY);
    return null;
  }
}

export function saveLatestPrediction(result, selectedFighters = {}) {
  if (!isBrowser()) return null;
  const generatedAt = new Date().toISOString();
  const statsA = result?.comparison?.stats1 || {};
  const statsB = result?.comparison?.stats2 || {};
  const payload = normalizeLatestPrediction({
    ...result,
    fighterA: selectedFighters.fighter_a || statsA,
    fighterB: selectedFighters.fighter_b || statsB,
    generatedAt,
    predictionKey:
      result?.prediction_id ||
      `${statsA.Name || selectedFighters.fighter_a?.name || "fighter-a"}::${statsB.Name || selectedFighters.fighter_b?.name || "fighter-b"}::${generatedAt}`,
  });

  if (!payload) return null;
  try {
    window.localStorage.setItem(LATEST_PREDICTION_KEY, JSON.stringify(payload));
    window.localStorage.removeItem(LEGACY_STORAGE_KEY);
    dispatchLatestPredictionEvent();
    return payload;
  } catch {
    return null;
  }
}

export function clearLatestPrediction() {
  if (!isBrowser()) return;
  try {
    window.localStorage.removeItem(LATEST_PREDICTION_KEY);
    window.localStorage.removeItem(LEGACY_STORAGE_KEY);
  } finally {
    dispatchLatestPredictionEvent();
  }
}

export function useLatestPrediction() {
  const [latest, setLatest] = useState(null);

  useEffect(() => {
    const refresh = () => setLatest(loadLatestPrediction());
    refresh();

    const onStorage = (event) => {
      if (!event.key || event.key === LATEST_PREDICTION_KEY) refresh();
    };
    window.addEventListener(LATEST_PREDICTION_EVENT, refresh);
    window.addEventListener("storage", onStorage);
    window.addEventListener("focus", refresh);
    window.addEventListener("pageshow", refresh);
    document.addEventListener("visibilitychange", refresh);
    return () => {
      window.removeEventListener(LATEST_PREDICTION_EVENT, refresh);
      window.removeEventListener("storage", onStorage);
      window.removeEventListener("focus", refresh);
      window.removeEventListener("pageshow", refresh);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, []);

  return latest;
}
