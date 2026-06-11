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

export function modelStatusLabel(status) {
  const value = String(status || "not_reported").toLowerCase();
  if (value === "high_confidence_only") return "High-confidence research signal";
  if (value === "production_candidate") return "Validated candidate signal";
  if (value === "experimental") return "Experimental insight";
  if (value === "weak_or_failed_baseline") return "Under review";
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
    return `FightScope's primary matchup signal leans toward ${winner}${confidence ? ` at ${confidence} confidence` : ""}. This is best read as a ${statusLabel}, not a final outcome claim.`;
  }
  if (id === "duration") {
    if (used || signalHasValue(signal)) {
      return "The duration read is active for this matchup and helps frame whether the fight profile points more toward a finish risk or a steadier decision path. Treat it as fight-shape context unless the full data-quality picture is strong.";
    }
    return "The duration read is shown for transparency, but FightScope is not using it as a strong standalone forecast for this matchup.";
  }
  if (id === "round") {
    if (used || signalHasValue(signal)) {
      return "The timing read looks for whether the fight is more consistent with an early danger window or a longer tactical build. It should be treated as a candidate signal rather than a final-grade round forecast.";
    }
    return "Round timing is not strong enough to drive this matchup read, so FightScope keeps it as supporting context only.";
  }
  if (id === "finish_type") {
    if (String(status).toLowerCase().includes("experimental")) {
      return "Finish-type context is still experimental. If it points toward striking, submission, or decision texture, use that as matchup color rather than a confident method prediction.";
    }
    return "Finish-type detail is available only when the method signal has enough support. For this matchup, FightScope keeps method texture cautious.";
  }
  if (id === "method") {
    return "Detailed method modeling is under review, so FightScope does not treat method probabilities as reliable. This card is shown for transparency only.";
  }
  if (id === "strike_volume") {
    return "The strike-volume signal describes likely activity and pace if the fight stays standing. Because this remains an experimental insight, it should be used as context rather than a hard strike-total projection.";
  }
  if (id === "takedown_control") {
    return "The takedown/control signal looks for grappling relevance, control pressure, and clinch-heavy exchange risk. It is useful context, but it should be weighed cautiously while the signal is still being validated.";
  }
  if (id === "market") {
    return "Market comparison is not active yet. FightScope has a research preview of timestamp-safe moneyline snapshots, but odds mapping and cutoff checks must pass before market-based reads are shown.";
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
