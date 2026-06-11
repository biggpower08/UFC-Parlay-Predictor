"use client";

const SIGNALS = [
  ["winner_model_signal", "winner_model", "Winner model"],
  ["elo_signal", "elo", "Elo"],
  ["finish_model_signal", "finish_model", "Finish"],
  ["method_model_signal", "method_model", "Method"],
  ["round_model_signal", "round_model", "Round phase"],
  ["strike_volume_signal", "strike_volume_model", "Strike volume"],
  ["takedown_control_signal", "takedown_control_model", "Takedown/control"],
  ["odds_calibration_signal", "odds_calibration_model", "Odds calibration"],
];

export default function ModelSignalGrid({ prediction, modelStatus, compact = false }) {
  const breakdown = prediction?.ensemble_breakdown || {};
  const unavailable = new Set(breakdown.unavailable_models || []);
  const models = modelStatus || {};

  return (
    <section className={compact ? "model-signal-panel compact" : "model-signal-panel"}>
      <div className="model-signal-heading">
        <div>
          <p className="eyebrow">Model signals</p>
          <h2>What contributed to this read</h2>
        </div>
        <p>Unavailable, weak, or blocked models are shown but kept out of scoring.</p>
      </div>
      <div className="model-signal-grid">
        {SIGNALS.map(([signalKey, modelKey, label]) => {
          const signal = breakdown[signalKey] || {};
          const model = models[modelKey] || {};
          const status = signal.status || signal.model_status || model.production_status || model.status || (unavailable.has(modelKey) ? "unavailable" : "not_reported");
          const used = Boolean(signal.used_in_score);
          const value = signal.probability ?? signal.value ?? signal.score ?? signal.signal ?? null;
          return (
            <article className={`model-signal-card ${statusClass(status)} ${used ? "used" : ""}`} key={signalKey}>
              <div>
                <strong>{label}</strong>
                <span className="model-status-badge">{used ? "used in score" : formatStatus(status)}</span>
              </div>
              {value !== null && value !== undefined && <b>{formatSignalValue(value)}</b>}
              <p>{signal.explanation || model.message || fallbackMessage(modelKey, status, used)}</p>
            </article>
          );
        })}
      </div>
      {unavailable.size > 0 && (
        <p className="model-unavailable-note">
          Unavailable models: {Array.from(unavailable).map((item) => item.replaceAll("_", " ")).join(", ")}.
        </p>
      )}
    </section>
  );
}

function formatSignalValue(value) {
  if (typeof value === "number") {
    if (Math.abs(value) <= 1) return `${Math.round(value * 100)}%`;
    return value.toFixed(2);
  }
  return String(value);
}

function formatStatus(status) {
  return String(status || "not reported").replaceAll("_", " ");
}

function statusClass(status) {
  const text = String(status || "").toLowerCase();
  if (text.includes("blocked") || text.includes("unavailable")) return "blocked";
  if (text.includes("weak") || text.includes("insufficient") || text.includes("not_trained")) return "limited";
  if (text.includes("experimental") || text.includes("candidate") || text.includes("high_confidence")) return "candidate";
  if (text.includes("trained") || text.includes("computed")) return "trained";
  return "limited";
}

function fallbackMessage(modelKey, status, used) {
  if (used) return "This signal was available for the final read.";
  if (modelKey === "odds_calibration_model") return "Odds remain research-only and are not used in scoring.";
  if (status === "not_reported") return "This signal was not reported for this matchup.";
  return "This signal is visible for context but was not used as a strong scoring factor.";
}
