"use client";

import {
  formatSignalValue,
  modelNarrative,
  modelStatusLabel,
  SIGNAL_SECTIONS,
  statusTone,
} from "../../lib/modelNarratives";

export default function ModelSignalGrid({ prediction, modelStatus, compact = false }) {
  const breakdown = prediction?.ensemble_breakdown || {};
  const unavailable = new Set(breakdown.unavailable_models || []);
  const models = modelStatus || {};

  return (
    <section className={compact ? "model-signal-panel compact" : "model-signal-panel"}>
      <div className="model-signal-heading">
        <div>
          <p className="eyebrow">Model reads</p>
          <h2>Signal-by-signal matchup view</h2>
        </div>
        <p>Each signal is labeled by readiness. Signals still under review are shown as context and do not get treated like final forecasts.</p>
      </div>
      {SIGNAL_SECTIONS.map((section) => (
        <div className="model-signal-section" key={section.title}>
          <h3>{section.title}</h3>
          <div className="model-signal-grid">
            {section.signals.map((config) => {
              const signal = breakdown[config.signalKey] || {};
              const model = models[config.modelKey] || {};
              const status =
                signal.status ||
                signal.model_status ||
                model.production_status ||
                model.status ||
                (unavailable.has(config.modelKey) ? "unavailable" : "not_reported");
              const used = Boolean(signal.used_in_score);
              const value = formatSignalValue(signal.probability ?? signal.value ?? signal.score ?? signal.signal ?? null);
              const tone = statusTone(status);
              return (
                <article className={`model-signal-card ${tone} ${used ? "used" : ""}`} key={config.id}>
                  <div className="model-signal-topline">
                    <strong>{config.title}</strong>
                    <span className="model-status-badge">{used ? "Included in read" : modelStatusLabel(status)}</span>
                  </div>
                  {value && <b>{value}</b>}
                  <p>{modelNarrative({ ...config, prediction, signal, model, status, used })}</p>
                  <small>{config.helper}</small>
                </article>
              );
            })}
          </div>
        </div>
      ))}
      {unavailable.size > 0 && (
        <p className="model-unavailable-note">
          Some supporting signals are not available for this matchup yet, so FightScope keeps them out of the final read.
        </p>
      )}
    </section>
  );
}
