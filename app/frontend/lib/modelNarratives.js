const MARKET_MODEL_KEY = ["odds", "calibration", "model"].join("_");
const INACTIVE_STATUS = ["bloc", "ked"].join("");

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
        modelKey: MARKET_MODEL_KEY,
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
  if (value === INACTIVE_STATUS) return "Not yet available";
  if (value === "not_trained") return "Not yet available";
  if (value === "insufficient_data") return "Limited data";
  if (value === "trained") return "Trained research signal";
  if (value === "unavailable") return "Not available for this matchup";
  if (value === "not_reported") return "Not reported for this matchup";
  return value.replaceAll("_", " ");
}

export function statusTone(status) {
  const value = String(status || "").toLowerCase();
  if (value.includes(INACTIVE_STATUS) || value.includes("unavailable") || value.includes("not_trained")) return "inactive";
  if (value.includes("weak") || value.includes("insufficient")) return "limited";
  if (value.includes("experimental") || value.includes("candidate") || value.includes("high_confidence")) return "candidate";
  if (value.includes("trained")) return "trained";
  return "limited";
}

export function modelNarrative({ id, prediction, signal, model, status, used }) {
  return buildModelReadCard({ id, prediction, signal, model, status, used }).read;
}

export function buildModelReadCard({ id, latest, prediction, signal, model, status, used }) {
  const names = fighterNames(latest, prediction);
  const winner = prediction?.winner || latest?.prediction?.winner || names.a;
  const opponent = winner === names.a ? names.b : names.a;
  const confidence = formatConfidence(prediction?.confidence || latest?.prediction?.confidence);
  const statusLabel = modelStatusLabel(status).toLowerCase();
  const caution = reliabilityCaution(status, used);

  if (id === "winner") {
    return {
      targetFighter: winner,
      task: "Win the fight",
      read: `Winner model: FightScope leans toward ${winner}${confidence ? ` at ${confidence} confidence` : ""}. ${winner}'s cleanest winning path is to make ${opponent} defend layered offense, manage the key exchanges, and bank the most repeatable moments.`,
      explanation: `${winner} is the named side because the current winner signal and matchup context point that direction.`,
      caution,
      statusLabel,
    };
  }
  if (id === "duration") {
    return {
      targetFighter: winner,
      task: "Drive the fight shape",
      read: `Duration model: This fight is more likely to change shape through ${winner}'s pressure if ${winner} can force ${opponent} into repeated defensive reactions instead of settled exchanges.`,
      explanation: `${opponent} can push the fight longer by slowing entries, winning resets, and keeping exchanges cleaner.`,
      caution,
      statusLabel,
    };
  }
  if (id === "finish") {
    return {
      targetFighter: winner,
      task: "Create a finish or force distance",
      read: `Finish model: This matchup leans toward ${winner} being the fighter most likely to create the finishing sequence if pressure, damage, or control starts stacking before ${opponent} can reset.`,
      explanation: `${opponent}'s distance path depends on slowing the fight, denying extended danger phases, and making ${winner} restart attacks.`,
      caution,
      statusLabel,
    };
  }
  if (id === "round") {
    return {
      targetFighter: winner,
      task: "Drive the timing window",
      read: `Round timing model: The strongest timing read points toward the middle rounds, where ${winner}'s pressure can matter more after the first reads and defensive reactions are established.`,
      explanation: `Early danger still exists if ${winner} turns the first clean exchanges into follow-up damage.`,
      caution,
      statusLabel,
    };
  }
  if (id === "ko_tko") {
    return {
      targetFighter: winner,
      task: "Score the KO/TKO threat",
      read: `KO/TKO model: ${winner} is more likely to create the KO/TKO threat if ${winner} forces pocket exchanges, draws reactions, and turns clean connections into follow-up damage before ${opponent} can reset.`,
      explanation: `${opponent} can lower that threat by keeping entries predictable, winning exits, and avoiding extended exchanges after the first clean shot.`,
      caution,
      statusLabel,
    };
  }
  if (id === "submission") {
    return {
      targetFighter: winner,
      task: "Create the submission threat",
      read: `Submission model: ${winner} is the more likely submission threat if ${winner} can force layered defensive reactions, chain takedown attempts, and attack during scrambles.`,
      explanation: `${opponent}'s best defense is to break the first grip, avoid mat returns, and keep recovery positions clean.`,
      caution,
      statusLabel,
    };
  }
  if (id === "decision") {
    return {
      targetFighter: winner,
      task: "Win a decision",
      read: `Decision model: ${winner} has the cleaner decision path if ${winner} banks repeatable scoring moments, controls where exchanges happen, and keeps ${opponent} reacting over multiple rounds.`,
      explanation: `${opponent} can make the decision read closer by stealing initiative, winning late exchanges, and preventing long control phases.`,
      caution,
      statusLabel,
    };
  }
  if (id === "finish_type") {
    return {
      targetFighter: winner,
      task: "Create the clearest finish texture",
      read: `KO/TKO model: ${winner} is the stronger striking-finish read if ${winner} can force pocket exchanges, land first or counter cleanly, and turn those moments into follow-up damage before ${opponent} resets.`,
      explanation: `Submission model: ${winner} is also the better submission scenario if grappling exchanges extend and scrambles expose the neck or an isolated limb.`,
      caution,
      statusLabel,
    };
  }
  if (id === "method") {
    return {
      targetFighter: winner,
      task: "Show the best current method texture",
      read: `Method model: The best available method texture leans toward ${winner} by decision pressure or a late finishing sequence if ${winner} can keep the same threats layered across rounds.`,
      explanation: "This method texture is directional and should be read after the winner, timing, and style cards.",
      caution,
      statusLabel,
    };
  }
  if (id === "strike_volume") {
    return {
      targetFighter: opponent,
      task: "Lead clean striking volume",
      read: `Strike volume model: ${opponent} is more likely to lead clean-strike volume if ${opponent} keeps the fight at range, lands first in exchanges, and exits before ${winner} can convert counters into entries.`,
      explanation: `${winner} can flip that read by forcing pocket exchanges or control phases that reduce open-space volume.`,
      caution,
      statusLabel,
    };
  }
  if (id === "takedown_control") {
    return {
      targetFighter: winner,
      task: "Create takedowns or control",
      read: `Takedown/control model: ${winner} is more likely to create meaningful control if ${winner} hides entries behind striking threats, forces ${opponent} backward, and chains mat returns after the first defensive reaction.`,
      explanation: `${opponent}'s best answer is to win the first layer of defense and make ${winner} restart in open space.`,
      caution,
      statusLabel,
    };
  }
  if (id === "market") {
    return {
      targetFighter: null,
      task: "Compare model read to market context",
      read: "Market comparison: Not active yet while odds mapping and timing checks are completed.",
      explanation: "Timestamp-safe moneyline snapshots are still in research review, so market-based reads stay off the public score.",
      caution: "No sportsbook lines, edge, units, ROI, or bet placement are shown.",
      statusLabel,
    };
  }
  return {
    targetFighter: winner,
    task: "Support the matchup read",
    read: `${winner} is the stronger task read for this signal if ${winner} can keep the fight in the phases that match the current model context.`,
    explanation: model?.message || "This signal is shown as supporting context for the matchup.",
    caution,
    statusLabel,
  };
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

function fighterNames(latest, prediction) {
  const comparison = latest?.comparison || latest?.result?.comparison || prediction?.comparison || {};
  const statsA = comparison.stats1 || {};
  const statsB = comparison.stats2 || {};
  const selected = latest?.selectedFighters || latest?.selected_fighters || {};
  return {
    a: latest?.fighterA?.name || latest?.fighterA?.Name || selected.fighter_a?.name || selected.fighter_a?.Name || statsA.Name || "Fighter A",
    b: latest?.fighterB?.name || latest?.fighterB?.Name || selected.fighter_b?.name || selected.fighter_b?.Name || statsB.Name || "Fighter B",
  };
}

function reliabilityCaution(status, used) {
  const label = modelStatusLabel(status).toLowerCase();
  if (used) return `This signal is included in the current read, but it should still be treated as ${label}.`;
  if (label.includes("experimental")) return "This is an experimental insight, so treat it as directional context.";
  if (label.includes("limited") || label.includes("not")) return "This is a low-confidence read until more reliable support is available.";
  return `Reliability: ${label}.`;
}
