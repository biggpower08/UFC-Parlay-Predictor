"use client";

import { Activity, Brain, RefreshCw, Search, ShieldCheck } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

const API_CANDIDATES = Array.from(
  new Set(
    [
      process.env.NEXT_PUBLIC_API_URL,
      process.env.NEXT_PUBLIC_API_BASE,
      "/api",
    ].filter(Boolean),
  ),
);

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

export default function App() {
  const [fighterA, setFighterA] = useState("Islam Makhachev");
  const [fighterB, setFighterB] = useState("Alex Pereira");
  const [suggestions, setSuggestions] = useState({ a: [], b: [] });
  const [activeTab, setActiveTab] = useState("matchup");
  const [result, setResult] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [resolver, setResolver] = useState(null);
  const [fighterMeta, setFighterMeta] = useState({ a: null, b: null });
  const [allowCrossDivision, setAllowCrossDivision] = useState(false);
  const [searching, setSearching] = useState({ a: false, b: false });

  useEffect(() => {
    checkHealth();
    if ("serviceWorker" in navigator) {
      navigator.serviceWorker.register("/service-worker.js").catch(() => {});
    }
  }, []);

  async function checkHealth() {
    try {
      const response = await apiFetch("/health", { cache: "no-store" });
      if (!response.ok) throw new Error(await readApiError(response));
      const data = await response.json();
      setHealth({ ...data, ok: true });
      setMessage("");
    } catch (error) {
      setHealth({ ok: false });
      setMessage(`Prediction engine is not connected: ${error.message}`);
    }
  }

  async function searchFighters(slot, value) {
    if (value.trim().length < 2) {
      setSuggestions((s) => ({ ...s, [slot]: [] }));
      return;
    }
    setSearching((current) => ({ ...current, [slot]: true }));
    try {
      const response = await apiFetch(`/fighters/search?q=${encodeURIComponent(value)}`);
      if (!response.ok) throw new Error(await readApiError(response));
      const data = await response.json();
      setSuggestions((s) => ({ ...s, [slot]: data.fighters || [] }));
    } catch (error) {
      setMessage(`Search failed: ${error.message}`);
    } finally {
      setSearching((current) => ({ ...current, [slot]: false }));
    }
  }

  async function predict() {
    setLoading(true);
    setMessage("");
    try {
      if (knownWeightClassMismatch() && !allowCrossDivision) {
        setMessage("These fighters are listed in different weight classes. Turn on cross-division matchups to continue.");
        return;
      }
      const resolvedA = await resolveBeforePrediction("a", fighterA);
      if (!resolvedA) return;
      const resolvedB = await resolveBeforePrediction("b", fighterB);
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
          allow_cross_division: allowCrossDivision,
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
        setMessage(problem.detail?.message || "This matchup is blocked by the weight class rule.");
        return;
      }
      if (!response.ok) throw new Error(await readApiError(response));
      const data = await response.json();
      setResult(data);
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
      const response = await apiFetch(`/fighters/resolve?q=${encodeURIComponent(value)}`);
      if (!response.ok) throw new Error(await readApiError(response));
      data = await response.json();
    } catch (error) {
      setMessage(`Name check failed: ${error.message}`);
      return null;
    }
    if (data.status === "resolved") {
      const best = data.candidates?.[0] || null;
      if (slot === "a") setFighterA(data.resolved_name);
      if (slot === "b") setFighterB(data.resolved_name);
      if (best) {
        setFighterMeta((current) => ({ ...current, [slot]: best }));
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
    if (resolver.slot === "a") setFighterA(name);
    if (resolver.slot === "b") setFighterB(name);
    if (picked) {
      setFighterMeta((current) => ({ ...current, [resolver.slot]: picked }));
    }
    setResolver(null);
    setMessage(`${name} selected. Press Predict again.`);
  }

  function knownWeightClassMismatch() {
    const classA = fighterMeta.a?.weight_class;
    const classB = fighterMeta.b?.weight_class;
    if (!classA || !classB || classA === "Unknown" || classB === "Unknown") return false;
    return classA !== classB;
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

  const confidence = useMemo(() => {
    if (!result) return 0;
    return Math.round((result.prediction.confidence || 0.5) * 100);
  }, [result]);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Local AI Fight Lab</p>
          <h1>UFC Predictor</h1>
        </div>
        <div className="status-stack">
          <div className={health?.ok ? "status online" : "status offline"}>
            <Activity size={18} />
            {health?.ok ? "Engine connected" : "Engine offline"}
          </div>
          <div className={health?.ollama?.available && health?.ollama?.model_loaded ? "status online" : "status"}>
            <Brain size={18} />
            {health?.ollama?.available && health?.ollama?.model_loaded ? "Ollama ready" : "Ollama unavailable"}
          </div>
        </div>
      </header>

      <section className="match-card">
        <FighterInput
          label="Fighter A"
          value={fighterA}
          onChange={(v) => {
            setFighterA(v);
            searchFighters("a", v);
          }}
          suggestions={suggestions.a}
          searching={searching.a}
          onPick={(name) => {
            const picked = suggestions.a.find((fighter) => fighter.name === name);
            setFighterA(name);
            setFighterMeta((current) => ({ ...current, a: picked || null }));
            setSuggestions((s) => ({ ...s, a: [] }));
          }}
        />
        <div className="versus">VS</div>
        <FighterInput
          label="Fighter B"
          value={fighterB}
          onChange={(v) => {
            setFighterB(v);
            searchFighters("b", v);
          }}
          suggestions={suggestions.b}
          searching={searching.b}
          onPick={(name) => {
            const picked = suggestions.b.find((fighter) => fighter.name === name);
            setFighterB(name);
            setFighterMeta((current) => ({ ...current, b: picked || null }));
            setSuggestions((s) => ({ ...s, b: [] }));
          }}
        />
        <button className="predict-button" onClick={predict} disabled={loading || health?.ok === false}>
          {loading ? <RefreshCw className="spin" size={20} /> : <Activity size={20} />}
          {loading ? "Analyzing" : "Predict Fight"}
        </button>
      </section>

      <section className="match-options panel">
        <div>
          <strong>Weight classes</strong>
          <span>
            {fighterMeta.a?.weight_class || "Fighter A unknown"} vs {fighterMeta.b?.weight_class || "Fighter B unknown"}
          </span>
        </div>
        {knownWeightClassMismatch() && (
          <p className="warning">These fighters are listed in different weight classes.</p>
        )}
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={allowCrossDivision}
            onChange={(event) => setAllowCrossDivision(event.target.checked)}
          />
          <span>Allow cross-division matchup</span>
        </label>
      </section>

      {message && (
        <div className="message">
          <span>{message}</span>
          {health?.ok === false && <button onClick={checkHealth}>Retry connection</button>}
        </div>
      )}

      {!result && (
        <section className="panel ready-panel">
          <div>
            <p className="eyebrow">Ready matchup</p>
            <h2>
              {fighterA || "Fighter A"} <span>vs</span> {fighterB || "Fighter B"}
            </h2>
          </div>
          <div className="ready-grid">
            <div>
              <strong>Name matching</strong>
              <span>Active</span>
            </div>
            <div>
              <strong>Local database</strong>
              <span>{health?.ok ? "Connected" : "Waiting"}</span>
            </div>
            <div>
              <strong>Web fill-in</strong>
              <span>{health?.ok ? "Available" : "Waiting"}</span>
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
                  if (resolver.slot === "a") setFighterA(e.target.value);
                  if (resolver.slot === "b") setFighterB(e.target.value);
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
            <button className={activeTab === "matchup" ? "active" : ""} onClick={() => setActiveTab("matchup")}>
              Matchup
            </button>
            <button className={activeTab === "prediction" ? "active" : ""} onClick={() => setActiveTab("prediction")}>
              Prediction
            </button>
            <button className={activeTab === "feedback" ? "active" : ""} onClick={() => setActiveTab("feedback")}>
              Feedback
            </button>
          </nav>

          {activeTab === "matchup" && <StatsPanel comparison={result.comparison} />}
          {activeTab === "prediction" && (
            <section className="panel prediction-panel">
              <div className="analyst-read">
                <span>Analyst read</span>
                <p>{result.summary}</p>
              </div>
              <div className="winner">
                <ShieldCheck size={28} />
                <span>{result.prediction.winner}</span>
              </div>
              <div className="confidence">
                <div style={{ width: `${confidence}%` }} />
              </div>
              <p className="confidence-label">{confidence}% confidence</p>
              <p className="reasoning">{result.prediction.reasoning}</p>
              <SignalGrid signals={result.prediction.signals || {}} />
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

function FighterInput({ label, value, onChange, suggestions, searching, onPick }) {
  return (
    <label className="fighter-input">
      <span>{label}</span>
      <div className="input-wrap">
        <Search size={18} />
        <input value={value} onChange={(e) => onChange(e.target.value)} />
      </div>
      {suggestions.length > 0 && (
        <div className="suggestions">
          {suggestions.map((fighter) => (
            <button key={fighter.name} onClick={() => onPick(fighter.name)}>
              <span>{fighter.name}</span>
              <small>{fighter.weight_class || `${fighter.wins ?? 0}-${fighter.losses ?? 0}`}</small>
            </button>
          ))}
        </div>
      )}
      {searching && <small className="searching">Searching...</small>}
    </label>
  );
}

function StatsPanel({ comparison }) {
  const rows = ["Elo", "Record", "Weight Class", "SLpM", "Str Acc %", "SApM", "Str Def %", "TD Avg", "TD Acc %", "TD Def %", "Reach (cm)", "Stance"];
  return (
    <section className="panel stats-grid">
      <h2>{comparison.stats1.Name}</h2>
      <h2>{comparison.stats2.Name}</h2>
      {rows.map((row) => (
        <div className="stat-row" key={row}>
          <span>{comparison.stats1[row]}</span>
          <b>{row}</b>
          <span>{comparison.stats2[row]}</span>
        </div>
      ))}
    </section>
  );
}

function SignalGrid({ signals }) {
  return (
    <div className="signal-grid">
      {Object.entries(signals).map(([name, signal]) => (
        <div className="signal" key={name}>
          <span>{name}</span>
          <strong>{Math.round((signal.prob_a || 0.5) * 100)}%</strong>
        </div>
      ))}
    </div>
  );
}
