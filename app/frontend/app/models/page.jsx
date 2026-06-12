"use client";

import { useLatestPrediction } from "../../lib/latestPrediction";
import { buildModelReadCard, modelStatusLabel, statusTone } from "../../lib/modelNarratives";

const MODEL_PAGE_SIGNALS = [
  { id: "winner", signalKey: "winner_model_signal", modelKey: "winner_model", title: "Winner model" },
  { id: "duration", signalKey: "finish_model_signal", modelKey: "fight_duration_model", title: "Fight shape / duration" },
  { id: "finish", signalKey: "finish_model_signal", modelKey: "finish_model", title: "Finish vs decision" },
  { id: "round", signalKey: "round_model_signal", modelKey: "round_model", title: "Round timing" },
  { id: "ko_tko", signalKey: "method_model_signal", modelKey: "finish_type_model", title: "KO/TKO read" },
  { id: "submission", signalKey: "method_model_signal", modelKey: "finish_type_model", title: "Submission read" },
  { id: "decision", signalKey: "method_model_signal", modelKey: "goes_distance_model", title: "Decision read" },
  { id: "strike_volume", signalKey: "strike_volume_signal", modelKey: "strike_volume_model", title: "Strike volume" },
  { id: "takedown_control", signalKey: "takedown_control_signal", modelKey: "takedown_control_model", title: "Takedown/control" },
  { id: "method", signalKey: "method_model_signal", modelKey: "method_model", title: "Method detail" },
  { id: "market", signalKey: "odds_calibration_signal", modelKey: ["odds", "calibration", "model"].join("_"), title: "Market comparison" },
];

export default function ModelsPage() {
  const latest = useLatestPrediction();

  if (!latest) {
    return (
      <main className="app-shell">
        <section className="panel empty-page">
          <p className="eyebrow">Models</p>
          <h1>Model Reads</h1>
          <p>No prediction yet. Generate a matchup on Home first.</p>
          <a className="analysis-link" href="/">Go to Home</a>
        </section>
      </main>
    );
  }

  const comparison = latest.comparison || latest.result?.comparison || {};
  const analysis = latest.analysis || {};
  const breakdown = latest.prediction?.ensemble_breakdown || {};
  const models = analysis.prop_model_status || {};
  const unavailable = new Set(breakdown.unavailable_models || []);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Signal-by-signal reads</p>
          <h1>{comparison.stats1?.Name || latest.fighterA?.name || "Fighter A"} vs {comparison.stats2?.Name || latest.fighterB?.name || "Fighter B"}</h1>
        </div>
      </header>

      <section className="panel model-page-intro">
        <div>
          <strong>Each model answers its own question.</strong>
          <span>These reads say who is more likely to accomplish the specific task and how they would probably do it.</span>
        </div>
        <a className="analysis-link subtle" href="/odds">Market status</a>
      </section>

      {analysis.matchup_type && (
        <section className="panel model-warning-card">
          <strong>{analysis.matchup_type.label}</strong>
          <span>{analysis.volatility_label || "Volatility"} context can make supporting model reads less stable.</span>
        </section>
      )}

      <section className="models-page-grid">
        {MODEL_PAGE_SIGNALS.map((config) => {
          const signal = breakdown[config.signalKey] || {};
          const model = models[config.modelKey] || {};
          const status =
            signal.status ||
            signal.model_status ||
            model.production_status ||
            model.status ||
            (unavailable.has(config.modelKey) ? "unavailable" : "not_reported");
          const used = Boolean(signal.used_in_score);
          const read = buildModelReadCard({ ...config, latest, prediction: latest.prediction, signal, model, status, used });
          return (
            <article className={`model-read-card ${statusTone(status)} ${used ? "used" : ""}`} key={config.id}>
              <div className="model-signal-topline">
                <strong>{config.title}</strong>
                <span className="model-status-badge">{used ? "Included in read" : modelStatusLabel(status)}</span>
              </div>
              <p className="read-direct">{read.read}</p>
              <p>{read.explanation}</p>
              <em>{read.caution}</em>
            </article>
          );
        })}
      </section>

      <section className="panel odds-status-panel">
        <div>
          <strong>Market comparison inactive</strong>
          <span>Odds mapping and timing checks are still in review, so market signals stay out of the public read.</span>
        </div>
      </section>
    </main>
  );
}
