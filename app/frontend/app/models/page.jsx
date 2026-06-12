"use client";

import { useLatestPrediction } from "../../lib/latestPrediction";
import { buildModelReadCard, modelStatusLabel, statusTone } from "../../lib/modelNarratives";
import { MODEL_READ_SIGNALS } from "../../lib/modelRegistry";

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
        {MODEL_READ_SIGNALS.map((config) => {
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
                <div>
                  <strong>{read.title}</strong>
                  <span>{read.category} · {read.modelType}</span>
                </div>
                <span className="model-status-badge">{used ? "Included in read" : modelStatusLabel(status)}</span>
              </div>
              <div className="model-task-line">
                <span>{read.task}</span>
                {read.targetFighter && <b>{read.targetFighter}</b>}
              </div>
              <p className="read-direct">{read.read}</p>
              <p>{read.explanation}</p>
              {read.evidence?.length > 0 && (
                <div className="model-evidence-list" aria-label={`${read.title} evidence`}>
                  {read.evidence.map((item) => <span key={item}>{item}</span>)}
                </div>
              )}
              {read.missingData?.length > 0 && (
                <p className="model-missing-data">Missing: {read.missingData.join(", ")}</p>
              )}
              {read.limitations?.length > 0 && (
                <ul className="model-limitations">
                  {read.limitations.map((item) => <li key={item}>{item}</li>)}
                </ul>
              )}
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
