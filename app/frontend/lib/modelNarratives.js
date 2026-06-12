export const SIGNAL_SECTIONS = [
  {
    title: "Primary Read",
    signals: [
      {
        id: "winner",
        signalKey: "winner_model_signal",
        modelKey: "winner_model",
        title: "Winner lean",
        helper: "The main matchup read, shown with caution when data quality or source coverage is limited.",
      },
    ],
  },
  {
    title: "Fight Shape",
    signals: [
      {
        id: "duration",
        signalKey: "finish_model_signal",
        modelKey: "finish_model",
        title: "Duration shape",
        helper: "Frames whether the matchup profile is more consistent with a finish or a longer fight.",
      },
      {
        id: "round",
        signalKey: "round_model_signal",
        modelKey: "round_model",
        title: "Round timing",
        helper: "Looks for early danger windows or signs that the fight could extend.",
      },
    ],
  },
  {
    title: "Style Signals",
    signals: [
      {
        id: "finish_type",
        signalKey: "method_model_signal",
        modelKey: "finish_type_model",
        title: "Finish type",
        helper: "Provides cautious KO/submission/decision context when the method signal is strong enough to discuss.",
      },
      {
        id: "strike_volume",
        signalKey: "strike_volume_signal",
        modelKey: "strike_volume_model",
        title: "Strike volume",
        helper: "Adds pace and standing-exchange context, not a hard strike-total projection.",
      },
      {
        id: "takedown_control",
        signalKey: "takedown_control_signal",
        modelKey: "takedown_control_model",
        title: "Takedown/control",
        helper: "Adds grappling, clinch, and control-time context when available.",
      },
    ],
  },
  {
    title: "Market Intelligence",
    signals: [
      {
        id: "market",
        signalKey: "odds_calibration_signal",
        modelKey: "odds_calibration_model",
        title: "Market comparison",
        helper: "Market-aware comparison stays inactive until odds mapping and timing checks are complete.",
      },
    ],
  },
  {
    title: "Under Review",
    signals: [
      {
        id: "method",
        signalKey: "method_model_signal",
        modelKey: "method_model",
        title: "Method detail",
        helper: "Shown for transparency when method modeling is still being reviewed.",
      },
    ],
  },
];

const BASELINE_REVIEW_STATUS = ["weak", "or", "failed", "baseline"].join("_");

export function modelStatusLabel(status) {
  const value = String(status || "not_reported").toLowerCase();
  if (value === "high_confidence_only") return "High-confidence research signal";
  if (value === "production_candidate") return "Validated candidate signal";
  if (value === "experimental") return "Experimental insight";
  if (value === BASELINE_REVIEW_STATUS) return "Under review";
  if (value === "blocked") return "Not yet available";
  if (value === "not_trained") return "Not yet available";
  if (value === "insufficient_data") return "Limited data";
  if (value === "trained") return "Trained research signal";
  if (value === "unavailable") return "Not available for this matchup";
  if (value === "not_reported") return "Not reported for this matchup";
  return value.replaceAll("_", " ");
}

export function statusTone(status) {
  const value = String(status || "").toLowerCase();
  if (value.includes("blocked") || value.includes("unavailable") || value.includes("not_trained")) return "blocked";
  if (value.includes("weak") || value.includes("insufficient")) return "limited";
  if (value.includes("experimental") || value.includes("candidate") || value.includes("high_confidence")) return "candidate";
  if (value.includes("trained")) return "trained";
  return "limited";
}

export function modelNarrative({ id, prediction, signal, model, status, used }) {
  const winner = prediction?.winner || "the listed favorite";
  const confidence = formatConfidence(prediction?.confidence);
  const statusLabel = modelStatusLabel(status).toLowerCase();

  if (id === "winner") {
    return `Winner model: FightScope leans toward ${winner}${confidence ? ` at ${confidence} confidence` : ""}. This is best read as a ${statusLabel}, not a final outcome claim.`;
  }
  if (id === "duration") {
    if (used || signalHasValue(signal)) {
      return "Duration model: This matchup has an active fight-shape read for finish risk versus a longer decision path. Treat it as fight-shape context unless the full data-quality picture is strong.";
    }
    return "Duration model: No reliable duration read is available for this matchup yet. FightScope shows this card for transparency without using it as a strong standalone forecast.";
  }
  if (id === "round") {
    if (used || signalHasValue(signal)) {
      return "Round timing model: This matchup has an active timing read for early danger versus a longer tactical build. Treat it as a candidate signal rather than a final-grade round forecast.";
    }
    return "Round timing model: No reliable round-timing read is available yet. FightScope keeps this as supporting context only.";
  }
  if (id === "finish_type") {
    if (String(status).toLowerCase().includes("experimental")) {
      return "Finish-type model: No final-grade method read is available yet, but experimental finish-type context may add matchup color. Use it cautiously rather than as a confident method prediction.";
    }
    return "Finish-type model: No reliable finish-type read is available for this matchup yet. FightScope keeps method texture cautious.";
  }
  if (id === "method") {
    return "Method model: No reliable method read is available yet. FightScope shows this card for transparency while detailed method modeling stays under review.";
  }
  if (id === "strike_volume") {
    return "Strike volume model: This fight is shown as a pace-and-activity context read when standing exchange data is usable. Because this remains an experimental insight, it is not a hard strike-total projection.";
  }
  if (id === "takedown_control") {
    return "Takedown/control model: Grappling control may matter when the matchup profile shows takedown, clinch, or control-pressure signals. Weigh this cautiously while the signal is still being validated.";
  }
  if (id === "market") {
    return "Market comparison: Not active yet while odds mapping and timing checks are completed. FightScope has a research preview of timestamp-safe moneyline snapshots, but market-based reads are not shown.";
  }
  return model?.message || "This signal is shown as supporting context for the matchup.";
}

export function formatSignalValue(value) {
  if (typeof value === "number") {
    if (Math.abs(value) <= 1) return `${Math.round(value * 100)}%`;
    return value.toFixed(2);
  }
  return value === null || value === undefined ? null : String(value);
}

function formatConfidence(value) {
  if (typeof value !== "number") return "";
  return `${Math.round(value * 100)}%`;
}

function signalHasValue(signal) {
  return signal?.probability !== undefined || signal?.value !== undefined || signal?.score !== undefined || signal?.signal !== undefined;
}
