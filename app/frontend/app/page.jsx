"use client";

import { Activity, RefreshCw, Search, ShieldCheck } from "lucide-react";
import { memo, useCallback, useEffect, useMemo, useRef, useState } from "react";
import ModelSignalGrid from "./components/ModelSignalGrid";
import { clearLatestPrediction, saveLatestPrediction } from "../lib/latestPrediction";

const API_CANDIDATES = Array.from(
  new Set(
    [
      "/api",
      process.env.NEXT_PUBLIC_API_URL,
      process.env.NEXT_PUBLIC_API_BASE,
    ].filter(Boolean),
  ),
);

const RESPONSE_CACHE = new Map();
const HEALTH_TTL_MS = 60_000;
const SEARCH_TTL_MS = 5 * 60_000;
const RESOLVE_TTL_MS = 5 * 60_000;

async function apiFetch(path, options = {}) {
  const errors = [];
  for (const base of API_CANDIDATES) {
    const url = `${base.replace(/\/$/, "")}${path}`;
    try {
      const response = await fetch(url, options);
      if (response.status < 500) return response;
      errors.push(`${url}: ${response.status} ${response.statusText}`);
    } catch (error) {
      errors.push(`${url}: ${error.message}`);
    }
  }
  throw new Error(errors.join(" | "));
}

async function apiFetchJson(path, options = {}) {
  const { ttl = 0, force = false, ...fetchOptions } = options;
  const cacheKey = `${path}:${JSON.stringify(fetchOptions.body || "")}`;
  const cached = RESPONSE_CACHE.get(cacheKey);
  if (!force && ttl > 0 && cached && Date.now() - cached.createdAt < ttl) {
    return cached.promise;
  }

  const promise = apiFetch(path, fetchOptions)
    .then(async (response) => {
      if (!response.ok) throw new Error(await readApiError(response));
      return response.json();
    })
    .catch((error) => {
      RESPONSE_CACHE.delete(cacheKey);
      throw error;
    });

  if (ttl > 0) {
    RESPONSE_CACHE.set(cacheKey, { createdAt: Date.now(), promise });
  }
  return promise;
}

function useDebouncedValue(value, delayMs) {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}

export default function App() {
  const [fighterAQuery, setFighterAQuery] = useState("");
  const [fighterBQuery, setFighterBQuery] = useState("");
  const [selectedFighterA, setSelectedFighterA] = useState(null);
  const [selectedFighterB, setSelectedFighterB] = useState(null);
  const [suggestions, setSuggestions] = useState({ a: [], b: [] });
  const [activeTab, setActiveTab] = useState("matchup");
  const [result, setResult] = useState(null);
  const [health, setHealth] = useState(null);
  const [creditStatus, setCreditStatus] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [resolver, setResolver] = useState(null);
  const [fighterMeta, setFighterMeta] = useState({ a: null, b: null });
  const [searching, setSearching] = useState({ a: false, b: false });
  const [activeSearchSlot, setActiveSearchSlot] = useState(null);
  const debouncedFighterA = useDebouncedValue(fighterAQuery, 300);
  const debouncedFighterB = useDebouncedValue(fighterBQuery, 300);
  const latestSearch = useRef({ a: "", b: "" });
  const userEditedSearch = useRef({ a: false, b: false });
  const searchRequestId = useRef({ a: 0, b: 0 });
  const appRef = useRef(null);

  const searchFighters = useCallback(async (slot, value) => {
    const trimmed = value.trim();
    latestSearch.current[slot] = trimmed;
    if (trimmed.length < 2) {
      setSuggestions((s) => ({ ...s, [slot]: [] }));
      setSearching((current) => ({ ...current, [slot]: false }));
      return;
    }
    const requestId = searchRequestId.current[slot] + 1;
    searchRequestId.current[slot] = requestId;
    setSearching((current) => ({ ...current, [slot]: true }));
    try {
      const data = await apiFetchJson(`/fighters/search?q=${encodeURIComponent(trimmed)}`, { ttl: SEARCH_TTL_MS });
      if (searchRequestId.current[slot] !== requestId || latestSearch.current[slot] !== trimmed) return;
      setSuggestions((s) => ({ ...s, [slot]: data.fighters || [] }));
    } catch (error) {
      setMessage(`Search failed: ${error.message}`);
    } finally {
      if (searchRequestId.current[slot] === requestId) {
        setSearching((current) => ({ ...current, [slot]: false }));
      }
    }
  }, []);

  useEffect(() => {
    checkHealth();
    loadCreditStatus();
    loadModelStatus();
    const closeSearchOnOutsideClick = (event) => {
      if (!event.target.closest?.(".fighter-input")) {
        setActiveSearchSlot(null);
      }
    };
    document.addEventListener("pointerdown", closeSearchOnOutsideClick);
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker
        .getRegistrations()
        .then((registrations) => Promise.all(registrations.map((registration) => registration.unregister())))
        .catch(() => {});
    }
    if ("caches" in window) {
      caches.keys().then((keys) => Promise.all(keys.map((key) => caches.delete(key)))).catch(() => {});
    }
    return () => document.removeEventListener("pointerdown", closeSearchOnOutsideClick);
  }, []);

  useEffect(() => {
    if (activeSearchSlot === "a" && userEditedSearch.current.a && debouncedFighterA === fighterAQuery) {
      searchFighters("a", debouncedFighterA);
    }
  }, [activeSearchSlot, debouncedFighterA, fighterAQuery, searchFighters]);

  useEffect(() => {
    if (activeSearchSlot === "b" && userEditedSearch.current.b && debouncedFighterB === fighterBQuery) {
      searchFighters("b", debouncedFighterB);
    }
  }, [activeSearchSlot, debouncedFighterB, fighterBQuery, searchFighters]);

  async function checkHealth(force = false) {
    try {
      const path = force ? "/health?force=true" : "/health";
      const data = await apiFetchJson(path, { cache: "no-store", ttl: HEALTH_TTL_MS, force });
      setHealth({ ...data, ok: Boolean(data.prediction_ready) });
      setMessage("");
    } catch (error) {
      setHealth({ ok: false });
      setMessage(`Prediction engine is not connected: ${error.message}`);
    }
  }

  async function loadCreditStatus() {
    try {
      const data = await apiFetchJson("/credits/status", { cache: "no-store", force: true });
      setCreditStatus(data);
    } catch {
      setCreditStatus(null);
    }
  }

  async function loadModelStatus() {
    try {
      const data = await apiFetchJson("/models/status", { cache: "no-store", force: true });
      setModelStatus(data.models || null);
    } catch {
      setModelStatus(null);
    }
  }

  async function predict() {
    setLoading(true);
    setMessage("");
    try {
      if (!canPredict) {
        setMessage("Search for and select two different fighters first.");
        return;
      }
      const resolvedA = await resolveBeforePrediction("a", selectedFighterA.name);
      if (!resolvedA) return;
      const resolvedB = await resolveBeforePrediction("b", selectedFighterB.name);
      if (!resolvedB) return;

      const response = await apiFetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          fighter_a: resolvedA,
          fighter_b: resolvedB,
          allow_scrape: true,
          confirmed_a: true,
          confirmed_b: true,
          allow_cross_division: true,
        }),
      });
      if (response.status === 409) {
        const problem = await response.json();
        setResolver({
          slot: "a",
          type: problem.detail?.status || "needs_confirmation",
          message: problem.detail?.message || "Please confirm the fighter.",
          candidates: problem.detail?.candidates || [],
        });
        return;
      }
      if (response.status === 422) {
        const problem = await response.json();
        setMessage(problem.detail?.message || "The prediction request could not be completed.");
        return;
      }
      if (response.status === 402) {
        const problem = await response.json();
        setMessage(problem.detail?.message || "You have used your free predictions. Buy prediction credits to continue.");
        return;
      }
      if (!response.ok) throw new Error(await readApiError(response));
      const data = await response.json();
      if (data.credit_status) setCreditStatus(data.credit_status);
      const saved = saveLatestPrediction(data, { fighter_a: fighterMeta.a || selectedFighterA, fighter_b: fighterMeta.b || selectedFighterB });
      setResult(saved?.result || data);
      setActiveTab("prediction");
    } catch (error) {
      setMessage(`Prediction failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }

  async function resolveBeforePrediction(slot, value) {
    let data;
    try {
      data = await apiFetchJson(`/fighters/resolve?q=${encodeURIComponent(value)}`, { ttl: RESOLVE_TTL_MS });
    } catch (error) {
      setMessage(`Name check failed: ${error.message}`);
      return null;
    }
    if (data.status === "resolved") {
      const best = data.candidates?.[0] || null;
      if (slot === "a") setFighterAQuery(data.resolved_name);
      if (slot === "b") setFighterBQuery(data.resolved_name);
      setActiveSearchSlot(null);
      if (best) {
        setFighterMeta((current) => ({ ...current, [slot]: best }));
        if (slot === "a") setSelectedFighterA(best);
        if (slot === "b") setSelectedFighterB(best);
      }
      return data.resolved_name;
    }
    setResolver({
      slot,
      type: data.status,
      message: data.message,
      candidates: data.candidates || [],
    });
    return null;
  }

  function pickResolved(name) {
    if (!resolver) return;
    const picked = resolver.candidates.find((fighter) => fighter.name === name) || null;
    setResult(null);
    if (resolver.slot === "a") {
      setFighterAQuery(name);
      setSelectedFighterA(picked || { name });
    }
    if (resolver.slot === "b") {
      setFighterBQuery(name);
      setSelectedFighterB(picked || { name });
    }
    if (picked) {
      setFighterMeta((current) => ({ ...current, [resolver.slot]: picked }));
    }
    setActiveSearchSlot(null);
    setResolver(null);
    setMessage(`${name} selected. Press Predict again.`);
  }

  function closeSearch(slot) {
    setActiveSearchSlot((current) => (current === slot ? null : current));
  }

  function pickFighter(slot, fighter) {
    setResult(null);
    const name = fighter.name;
    if (slot === "a") {
      setFighterAQuery(name);
      setSelectedFighterA(fighter);
    }
    if (slot === "b") {
      setFighterBQuery(name);
      setSelectedFighterB(fighter);
    }
    userEditedSearch.current[slot] = false;
    latestSearch.current[slot] = "";
    searchRequestId.current[slot] += 1;
    setFighterMeta((current) => ({ ...current, [slot]: fighter || null }));
    setSuggestions((current) => ({ ...current, [slot]: [] }));
    setSearching((current) => ({ ...current, [slot]: false }));
    closeSearch(slot);
  }

  function handleFighterInput(slot, value) {
    if (slot === "a") {
      setFighterAQuery(value);
      setSelectedFighterA(null);
    }
    if (slot === "b") {
      setFighterBQuery(value);
      setSelectedFighterB(null);
    }
    setResult(null);
    setActiveTab("matchup");
    setResolver(null);
    setMessage("");
    setFighterMeta((current) => ({ ...current, [slot]: null }));
    userEditedSearch.current[slot] = true;
    latestSearch.current[slot] = value.trim();
    searchRequestId.current[slot] += 1;
    setSuggestions((current) => ({ ...current, [slot]: [] }));
    if (value.trim().length < 2) {
      setSearching((current) => ({ ...current, [slot]: false }));
    }
    setActiveSearchSlot(value.trim().length >= 2 ? slot : null);
  }

  function handleFighterKeyDown(slot, event) {
    if (event.key !== "Enter") return;
    event.preventDefault();
    const first = suggestions[slot]?.[0];
    if (first && activeSearchSlot === slot) {
      pickFighter(slot, first);
      return;
    }
    closeSearch(slot);
  }

  function handleFighterBlur(slot, event) {
    if (event.currentTarget.contains(event.relatedTarget)) return;
    closeSearch(slot);
  }

  async function saveFeedback(wasCorrect) {
    if (!result) return;
    const predicted = result.prediction.winner;
    const actual = wasCorrect ? predicted : window.prompt("Actual winner?") || "";
    await apiFetch("/feedback", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        prediction_id: result.prediction_id,
        fighter_a: result.comparison.stats1.Name,
        fighter_b: result.comparison.stats2.Name,
        predicted_winner: predicted,
        actual_winner: actual,
        confidence: result.prediction.confidence,
        was_correct: wasCorrect,
        user_notes: "",
      }),
    });
    setMessage("Feedback saved.");
  }

  function clearCurrentLatestPrediction() {
    clearLatestPrediction();
    setResult(null);
    setActiveTab("matchup");
    setMessage("Latest prediction cleared.");
  }

  const confidence = useMemo(() => {
    if (!result) return 0;
    return Math.round((result.prediction.confidence || 0.5) * 100);
  }, [result]);
  const canPredict = Boolean(
    selectedFighterA?.name &&
      selectedFighterB?.name &&
      selectedFighterA.name !== selectedFighterB.name &&
      health?.prediction_ready !== false,
  );
  const readyTitle = selectedFighterA?.name && selectedFighterB?.name
    ? `${selectedFighterA.name} vs ${selectedFighterB.name}`
    : "Search for two fighters to generate a prediction.";
  const matchupType = result?.analysis?.matchup_type || localMatchupType(fighterMeta.a, fighterMeta.b);

  return (
    <main className="app-shell" ref={appRef}>
      <header className="topbar">
        <div>
          <p className="eyebrow">AI UFC and MMA matchup intelligence</p>
          <h1>FightScope</h1>
          <p className="hero-copy">
            A cyberpunk fight-intelligence scroll for winner predictions, confidence, Elo context, matchup stats, and honest model-informed reads.
          </p>
        </div>
        <div className="intro-sigil" aria-hidden="true">
          <span />
          <b>FS</b>
          <small>scan</small>
        </div>
        <div className="status-stack">
          <CreditBalanceBadge creditStatus={creditStatus} />
          <div className={health?.ok ? "status online" : "status offline"}>
            <Activity size={18} />
            {health?.ok ? "Engine connected" : "Engine offline"}
          </div>
        </div>
      </header>

      <section className="match-card">
        <FighterInput
          label="Fighter A"
          value={fighterAQuery}
          placeholder="Type fighter name here"
          onChange={(v) => handleFighterInput("a", v)}
          onFocus={() => {
            if (fighterAQuery.trim().length >= 2) setActiveSearchSlot("a");
          }}
          onBlur={(event) => handleFighterBlur("a", event)}
          onKeyDown={(event) => handleFighterKeyDown("a", event)}
          suggestions={activeSearchSlot === "a" ? suggestions.a : []}
          searching={searching.a}
          showDropdown={activeSearchSlot === "a" && fighterAQuery.trim().length >= 2}
          onPick={(fighter) => pickFighter("a", fighter)}
        />
        <div className="versus">VS</div>
        <FighterInput
          label="Fighter B"
          value={fighterBQuery}
          placeholder="Type fighter name here"
          onChange={(v) => handleFighterInput("b", v)}
          onFocus={() => {
            if (fighterBQuery.trim().length >= 2) setActiveSearchSlot("b");
          }}
          onBlur={(event) => handleFighterBlur("b", event)}
          onKeyDown={(event) => handleFighterKeyDown("b", event)}
          suggestions={activeSearchSlot === "b" ? suggestions.b : []}
          searching={searching.b}
          showDropdown={activeSearchSlot === "b" && fighterBQuery.trim().length >= 2}
          onPick={(fighter) => pickFighter("b", fighter)}
        />
        <button className="predict-button" onClick={predict} disabled={loading || !canPredict}>
          {loading ? <RefreshCw className="spin" size={20} /> : <Activity size={20} />}
          {loading ? "Analyzing" : canPredict ? "Predict Fight" : "Select two fighters"}
        </button>
      </section>

      <section className="matchup-strip">
        <span>
          {fighterMeta.a?.weight_class || "Unknown"} vs {fighterMeta.b?.weight_class || "Unknown"}
        </span>
        <b className={`matchup-mini-badge ${matchupType.severity}`}>{compactMatchupLabel(matchupType)}</b>
      </section>

      {loading && (
        <section className="loading-scroll" aria-live="polite">
          <div className="loading-kata" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>
          <div>
            <strong>Reading the matchup scroll</strong>
            <p>Checking available signals while keeping unavailable market and support models out of the read.</p>
          </div>
        </section>
      )}

      {message && (
        <div className="message">
          <span>{message}</span>
          {health?.prediction_ready === false && <button onClick={() => checkHealth(true)}>Retry connection</button>}
        </div>
      )}

      {!result && (
        <section className="panel ready-panel">
          <div>
            <p className="eyebrow">Ready matchup</p>
            <h2>
              {readyTitle}
            </h2>
            {!selectedFighterA || !selectedFighterB ? (
              <p className="helper-text">Start typing a fighter name, nickname, or partial name.</p>
            ) : null}
          </div>
          <div className="ready-grid">
            <div>
              <strong>Name matching</strong>
              <span>Active</span>
            </div>
            <div>
              <strong>Local database</strong>
              <span>{health?.database_ready ? "Connected" : "Waiting"}</span>
            </div>
            <div>
              <strong>Prediction model</strong>
              <span>{health?.sklearn_model ? "Available" : "Waiting"}</span>
            </div>
          </div>
        </section>
      )}

      {resolver && (
        <section className="resolver panel">
          <h2>{resolver.type === "needs_full_name" ? "Enter the full fighter name" : "Confirm fighter"}</h2>
          <p>{resolver.message}</p>
          {resolver.type === "needs_full_name" && (
            <div className="resolver-entry">
              <input
                autoFocus
                placeholder="Full fighter name"
                onChange={(e) => {
                  if (resolver.slot === "a") setFighterAQuery(e.target.value);
                  if (resolver.slot === "b") setFighterBQuery(e.target.value);
                }}
              />
              <button onClick={() => setResolver(null)}>Use this name</button>
            </div>
          )}
          {resolver.candidates.length > 0 && (
            <div className="candidate-grid">
              {resolver.candidates.map((fighter) => (
                <button key={fighter.name} onClick={() => pickResolved(fighter.name)}>
                  <strong>{fighter.name}</strong>
                  <span>{fighter.nickname ? `"${fighter.nickname}"` : "No nickname listed"}</span>
                  <small>{fighter._match_type?.replace("_", " ")} match</small>
                </button>
              ))}
            </div>
          )}
        </section>
      )}

      {result && (
        <>
          <nav className="tabs">
            <button className={activeTab === "prediction" ? "active" : ""} onClick={() => setActiveTab("prediction")}>
              Prediction
            </button>
            <button className={activeTab === "feedback" ? "active" : ""} onClick={() => setActiveTab("feedback")}>
              Feedback
            </button>
          </nav>

          {activeTab === "prediction" && (
            <section className="panel prediction-panel">
              {result.analysis && (
                <div className="analysis-badges">
                  <span>{result.analysis.confidence_label}</span>
                  <span>{result.analysis.volatility_label} volatility</span>
                  <span>{result.analysis.data_quality_label} data</span>
                  {result.analysis.matchup_type && (
                    <span className={`matchup-badge ${result.analysis.matchup_type.severity}`}>
                      {result.analysis.matchup_type.label}
                    </span>
                  )}
                </div>
              )}
              <div className="winner">
                <ShieldCheck size={28} />
                <span>{result.prediction.winner}</span>
              </div>
              <div className="confidence">
                <div style={{ width: `${confidence}%` }} />
              </div>
              <p className="confidence-label">{confidence}% confidence</p>
              <p className="reasoning">{result.prediction.reasoning}</p>
              <div className="analyst-read">
                <span>Analyst summary</span>
                <p>{summaryPreview(result.analysis?.summary || result.summary)}</p>
              </div>
              <div className="deep-link-grid">
                <a href="/analysis">Full Analysis</a>
                <a href="/stats">Matchup Stats</a>
                <a href="/odds">Odds / Betting Reads</a>
              </div>
              <ModelSignalGrid prediction={result.prediction} modelStatus={modelStatus || result.analysis?.prop_model_status} compact />
              <button className="analysis-link" type="button" onClick={clearCurrentLatestPrediction}>
                Clear latest prediction
              </button>
            </section>
          )}
          {activeTab === "feedback" && (
            <section className="panel feedback-panel">
              <h2>Was the prediction right?</h2>
              <div className="feedback-actions">
                <button onClick={() => saveFeedback(true)}>Correct</button>
                <button onClick={() => saveFeedback(false)}>Wrong</button>
              </div>
            </section>
          )}
        </>
      )}
    </main>
  );
}

async function readApiError(response) {
  try {
    const payload = await response.json();
    return payload.detail?.message || payload.detail || payload.message || response.statusText;
  } catch {
    return response.statusText || "Request failed";
  }
}

function localMatchupType(fighterA, fighterB) {
  const classA = fighterA?.weight_class;
  const classB = fighterB?.weight_class;
  if (!fighterA || !fighterB) {
    return {
      label: "Weight-class data incomplete",
      severity: "soft",
      explanation: "Select two fighters to preview matchup context.",
    };
  }
  if (missingWeightClass(classA) || missingWeightClass(classB)) {
    return {
      label: "Weight-class data incomplete",
      severity: "soft",
      explanation: "One or both fighters are missing reliable weight-class data, so confidence may be lower.",
    };
  }
  const normalizedA = normalizeWeightClass(classA);
  const normalizedB = normalizeWeightClass(classB);
  if (normalizedA === normalizedB) {
    return {
      label: "Same-division matchup",
      severity: "none",
      explanation: "Both fighters are listed in the same division.",
    };
  }
  const order = ["strawweight", "flyweight", "bantamweight", "featherweight", "lightweight", "welterweight", "middleweight", "light heavyweight", "heavyweight"];
  const indexA = order.indexOf(normalizedA);
  const indexB = order.indexOf(normalizedB);
  if (indexA === -1 || indexB === -1 || Math.abs(indexA - indexB) <= 1) {
    return {
      label: "Potential cross-division matchup",
      severity: "soft",
      explanation: "These fighters are listed near different or uncertain divisions, so the model may be less confident.",
    };
  }
  return {
    label: "Cross-division matchup",
    severity: "high",
    explanation: "These fighters are listed in different divisions. The prediction is still shown, but matchup realism and confidence may be lower.",
  };
}

function missingWeightClass(value) {
  return !value || ["unknown", "n/a", "na", "none", "null"].includes(String(value).trim().toLowerCase());
}

function normalizeWeightClass(value) {
  return String(value || "")
    .trim()
    .toLowerCase()
    .replace(/^women'?s\s+/, "");
}

function compactMatchupLabel(matchupType) {
  if (matchupType.label === "Same-division matchup") return "Same division";
  if (matchupType.label === "Potential cross-division matchup") return "Possibly cross-division";
  if (matchupType.label === "Cross-division matchup") return "Cross-division";
  return "Weight class unknown";
}

function summaryPreview(text) {
  if (!text) return "Open the full Analysis page for the deeper matchup breakdown.";
  const sentences = String(text).match(/[^.!?]+[.!?]+/g) || [String(text)];
  return sentences.slice(0, 3).join(" ").trim();
}

function CreditBalanceBadge({ creditStatus }) {
  if (!creditStatus) {
    return <div className="status credit-status">3 free predictions included</div>;
  }
  if (!creditStatus.enabled) {
    return <div className="status credit-status">{creditStatus.free_prediction_limit} free predictions included</div>;
  }
  return (
    <div className="status credit-status">
      {creditStatus.free_predictions_remaining} free / {creditStatus.credits_remaining} credits
    </div>
  );
}

const FighterInput = memo(function FighterInput({
  label,
  value,
  onChange,
  placeholder,
  onFocus,
  onBlur,
  onKeyDown,
  suggestions,
  searching,
  showDropdown,
  onPick,
}) {
  return (
    <label className="fighter-input" onBlur={onBlur}>
      <span>{label}</span>
      <div className="input-wrap">
        <Search size={18} />
        <input
          value={value}
          placeholder={placeholder}
          onChange={(e) => onChange(e.target.value)}
          onFocus={onFocus}
          onKeyDown={onKeyDown}
        />
      </div>
      {showDropdown && (suggestions.length > 0 || searching) && (
        <div className="suggestions">
          {suggestions.map((fighter) => (
            <button key={fighter.name} type="button" onClick={() => onPick(fighter)}>
              <span>{fighter.name}</span>
              <small>{fighter.weight_class || `${fighter.wins ?? 0}-${fighter.losses ?? 0}`}</small>
            </button>
          ))}
          {searching && suggestions.length === 0 && <div className="suggestion-note">Searching...</div>}
        </div>
      )}
    </label>
  );
});
