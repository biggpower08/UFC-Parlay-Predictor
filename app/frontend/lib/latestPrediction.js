"use client";

import { useEffect, useState } from "react";

export const LATEST_PREDICTION_KEY = "ufc_latest_prediction_v2";
export const LATEST_PREDICTION_EVENT = "ufc_latest_prediction_updated";
const SCHEMA_VERSION = 2;
const OLD_STORAGE_KEYS = ["latestPredictionResult", "latestPrediction", "latest_prediction", "ufc_latest_prediction", "ufc_latest_prediction_v1"];

function isBrowser() {
  return typeof window !== "undefined";
}

function dispatchLatestPredictionEvent(latestPrediction = null) {
  if (!isBrowser()) return;
  window.dispatchEvent(new CustomEvent(LATEST_PREDICTION_EVENT, { detail: latestPrediction }));
}

function removeOldPredictionKeys() {
  if (!isBrowser()) return;
  OLD_STORAGE_KEYS.forEach((key) => window.localStorage.removeItem(key));
}

function normalizeLatestPrediction(raw) {
  if (!raw || typeof raw !== "object") return null;
  const source = raw.result && typeof raw.result === "object" ? raw.result : raw;
  if (!source.prediction || !source.comparison) return null;

  const statsA = source.comparison?.stats1 || {};
  const statsB = source.comparison?.stats2 || {};
  if (!statsA.Name || !statsB.Name || !source.prediction?.winner) return null;
  const analysis = source.analysis || raw.analysis || {};
  const generatedAt = raw.generatedAt || raw.saved_at || new Date().toISOString();
  if (!isValidIsoDate(generatedAt)) return null;
  const fighterA = raw.fighterA || raw.selectedFighters?.fighter_a || raw.selected_fighters?.fighter_a || statsA;
  const fighterB = raw.fighterB || raw.selectedFighters?.fighter_b || raw.selected_fighters?.fighter_b || statsB;
  const predictionId =
    raw.predictionId ||
    raw.predictionKey ||
    source.prediction_id ||
    raw.prediction_id ||
    `${statsA.Name || fighterA?.name || "fighter-a"}::${statsB.Name || fighterB?.name || "fighter-b"}::${generatedAt}`;
  const matchupLabel = analysis.matchup_type?.label || "";
  const weightClassDisplay = `${statsA["Weight Class"] || fighterA?.weight_class || "Unknown"} vs ${statsB["Weight Class"] || fighterB?.weight_class || "Unknown"}`;

  return {
    ...source,
    schemaVersion: SCHEMA_VERSION,
    predictionId,
    generatedAt,
    fighterA,
    fighterB,
    matchupLabel,
    weightClassDisplay,
    result: source,
    analysis,
    stats: source.comparison,
    propReads: analysis.prop_reads || raw.propReads || [],
    confidence: source.prediction?.confidence ?? raw.confidence ?? null,
    volatility: analysis.volatility_label ?? raw.volatility ?? null,
    dataQuality: analysis.data_quality_label ?? raw.dataQuality ?? null,
    matchupType: analysis.matchup_type ?? raw.matchupType ?? null,
    selectedFighters: {
      fighter_a: fighterA,
      fighter_b: fighterB,
    },
  };
}

export function loadLatestPrediction() {
  if (!isBrowser()) return null;
  try {
    removeOldPredictionKeys();
    const saved = window.localStorage.getItem(LATEST_PREDICTION_KEY);
    if (!saved) return null;
    const parsed = JSON.parse(saved);
    if (parsed?.schemaVersion !== SCHEMA_VERSION) {
      window.localStorage.removeItem(LATEST_PREDICTION_KEY);
      return null;
    }
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

function isValidIsoDate(value) {
  if (!value || typeof value !== "string") return false;
  const timestamp = Date.parse(value);
  return Number.isFinite(timestamp);
}

export function saveLatestPrediction(result, selectedFighters = {}) {
  if (!isBrowser()) return null;
  const generatedAt = new Date().toISOString();
  const statsA = result?.comparison?.stats1 || {};
  const statsB = result?.comparison?.stats2 || {};
  const payload = normalizeLatestPrediction({
    result,
    fighterA: selectedFighters.fighter_a || statsA,
    fighterB: selectedFighters.fighter_b || statsB,
    generatedAt,
    predictionId:
      result?.prediction_id ||
      `${statsA.Name || selectedFighters.fighter_a?.name || "fighter-a"}::${statsB.Name || selectedFighters.fighter_b?.name || "fighter-b"}::${generatedAt}`,
  });

  if (!payload) return null;
  try {
    window.localStorage.setItem(LATEST_PREDICTION_KEY, JSON.stringify(payload));
    removeOldPredictionKeys();
    dispatchLatestPredictionEvent(payload);
    return payload;
  } catch {
    return null;
  }
}

export function clearLatestPrediction() {
  if (!isBrowser()) return;
  try {
    window.localStorage.removeItem(LATEST_PREDICTION_KEY);
    removeOldPredictionKeys();
  } finally {
    dispatchLatestPredictionEvent(null);
  }
}

export function useLatestPrediction() {
  const [latest, setLatest] = useState(null);

  useEffect(() => {
    const refresh = () => setLatest(loadLatestPrediction());
    refresh();

    const onLatestUpdated = (event) => {
      setLatest(event.detail || loadLatestPrediction());
    };
    const onStorage = (event) => {
      if (!event.key || event.key === LATEST_PREDICTION_KEY || OLD_STORAGE_KEYS.includes(event.key)) refresh();
    };
    window.addEventListener(LATEST_PREDICTION_EVENT, onLatestUpdated);
    window.addEventListener("storage", onStorage);
    window.addEventListener("focus", refresh);
    window.addEventListener("pageshow", refresh);
    document.addEventListener("visibilitychange", refresh);
    return () => {
      window.removeEventListener(LATEST_PREDICTION_EVENT, onLatestUpdated);
      window.removeEventListener("storage", onStorage);
      window.removeEventListener("focus", refresh);
      window.removeEventListener("pageshow", refresh);
      document.removeEventListener("visibilitychange", refresh);
    };
  }, []);

  return latest;
}
