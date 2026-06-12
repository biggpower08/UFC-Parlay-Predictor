import { modelDefinitionFor, SIGNAL_SECTIONS } from "./modelRegistry";

const INACTIVE_STATUS = ["bloc", "ked"].join("");
const BASELINE_REVIEW_STATUS = ["weak", "or", "failed", "baseline"].join("_");

export { SIGNAL_SECTIONS };

export function modelStatusLabel(status) {
  const value = String(status || "not_reported").toLowerCase();
  if (value === "high_confidence_only") return "High-confidence only";
  if (value === "production_candidate") return "Production candidate";
  if (value === "experimental") return "Experimental context";
  if (value === BASELINE_REVIEW_STATUS) return "Weak signal";
  if (value === INACTIVE_STATUS) return "Blocked";
  if (value === "not_trained") return "Not trained";
  if (value === "insufficient_data") return "Limited data";
  if (value === "trained") return "Trained research signal";
  if (value === "unavailable") return "Unavailable for this matchup";
  if (value === "not_reported") return "Not reported";
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

export function buildModelReadCard({ id, latest, prediction, signal = {}, model = {}, status, used }) {
  const definition = modelDefinitionFor(id);
  const names = fighterNames(latest, prediction);
  const stats = fighterStats(latest, prediction);
  const winner = prediction?.winner || latest?.prediction?.winner || names.a;
  const opponent = sameName(winner, names.a) ? names.b : names.a;
  const effectiveStatus = status || signal.status || signal.model_status || model.production_status || model.status || definition.defaultStatus;
  const statusLabel = modelStatusLabel(effectiveStatus);
  const confidenceScore = numericConfidence(prediction?.confidence ?? latest?.prediction?.confidence ?? signal.probability ?? signal.score);
  const confidenceLabel = confidenceText(confidenceScore, effectiveStatus);
  const dataQuality = dataQualityText(latest, prediction, model);
  const updatedAt = model.trained_at || model.updated_at || latest?.generatedAt || latest?.prediction?.generatedAt || null;
  const isBlocked = statusTone(effectiveStatus) === "inactive";
  const isTrained = ["trained", "production_candidate", "high_confidence_only"].includes(String(effectiveStatus).toLowerCase());
  const isHeuristic = !isTrained && !isBlocked;
  const missingData = missingDataList(signal, model, effectiveStatus);
  const base = {
    id: definition.id,
    title: definition.title,
    category: definition.category,
    modelType: definition.modelType,
    status: effectiveStatus || "not_reported",
    statusLabel,
    targetFighter: winner,
    opponentFighter: opponent,
    task: definition.task,
    confidenceLabel,
    confidenceScore,
    isTrained,
    isHeuristic,
    isBlocked,
    isAvailable: !isBlocked && effectiveStatus !== "unavailable" && effectiveStatus !== "not_trained",
    dataQuality,
    missingData,
    updatedAt,
    evidence: evidenceFor({ id, latest, prediction, signal, model, used, names, stats, confidenceScore }),
    limitations: limitationsFor(effectiveStatus, model),
  };

  if (id === "winner") {
    return finalizeCard({
      ...base,
      targetFighter: winner,
      opponentFighter: opponent,
      read: `${winner} is the current win read.`,
      explanation: `${winner} is favored by the current matchup signal when FightScope combines the main winner read, Elo context, and available supporting model signals. The useful interpretation is not certainty; it is that ${winner} owns the cleaner repeatable path right now.`,
    }, used);
  }

  if (id === "duration") {
    const finishSide = winner;
    return finalizeCard({
      ...base,
      targetFighter: finishSide,
      opponentFighter: opponent,
      read: `${finishSide} is the fighter more likely to make the fight shape unstable.`,
      explanation: `${finishSide}'s duration path comes from stacking pressure, damage, or control before ${opponent} can settle the pace. ${opponent}'s cleaner answer is to slow entries, win resets, and make the fight repeatable over rounds.`,
    }, used);
  }

  if (id === "finish") {
    return finalizeCard({
      ...base,
      targetFighter: winner,
      opponentFighter: opponent,
      read: `${winner} is the stronger finish-pressure read.`,
      explanation: `${winner} is the side more likely to turn a winning phase into a stoppage sequence if the same threat keeps repeating. This card supports finish-vs-decision texture only; it does not claim an exact method or round.`,
    }, used);
  }

  if (id === "round") {
    return finalizeCard({
      ...base,
      targetFighter: winner,
      opponentFighter: opponent,
      read: `${winner} has the clearer middle-phase pressure read.`,
      explanation: `The round signal is most useful as timing context: early reads matter, but the matchup becomes more informative once entries, counters, and defensive reactions have repeated. Treat this as a phase read, not an exact-round call.`,
    }, used);
  }

  if (id === "ko_tko") {
    return finalizeCard({
      ...base,
      targetFighter: winner,
      opponentFighter: opponent,
      read: `${winner} is the more useful KO/TKO threat to watch.`,
      explanation: `${winner}'s striking-finish path depends on forcing exchanges where a clean shot can become a follow-up sequence. ${opponent} reduces that risk by exiting after the first exchange and avoiding repeated pocket moments.`,
    }, used);
  }

  if (id === "submission") {
    return finalizeCard({
      ...base,
      targetFighter: winner,
      opponentFighter: opponent,
      read: `${winner} is the more useful submission threat to watch.`,
      explanation: `${winner}'s submission path appears when grappling exchanges extend, scrambles expose the neck or an isolated limb, or control phases make ${opponent} defend in layers. This remains context until method modeling is stronger.`,
    }, used);
  }

  if (id === "decision") {
    return finalizeCard({
      ...base,
      targetFighter: winner,
      opponentFighter: opponent,
      read: `${winner} has the cleaner decision path.`,
      explanation: `${winner}'s decision route is to bank repeatable scoring moments, keep the fight in manageable phases, and make ${opponent} spend more time reacting than initiating.`,
    }, used);
  }

  if (id === "strike_volume") {
    const volumeFighter = pickHigherStat(stats.a, stats.b, ["SLpM", "sig_str_landed_per_min", "Sig. Str. LPM"], names, winner);
    const volumeOpponent = sameName(volumeFighter, names.a) ? names.b : names.a;
    return finalizeCard({
      ...base,
      targetFighter: volumeFighter,
      opponentFighter: volumeOpponent,
      read: `${volumeFighter} is the cleaner strike-volume read.`,
      explanation: `${volumeFighter} is the side to watch for volume if the fight stays in open-space exchanges. ${volumeOpponent} can flip that texture with clinch time, mat returns, or pressure that collapses range.`,
    }, used);
  }

  if (id === "takedown_control") {
    const controlFighter = pickHigherStat(stats.a, stats.b, ["TD Avg.", "td_avg", "takedown_avg"], names, winner);
    const controlOpponent = sameName(controlFighter, names.a) ? names.b : names.a;
    return finalizeCard({
      ...base,
      targetFighter: controlFighter,
      opponentFighter: controlOpponent,
      read: `${controlFighter} is the stronger takedown/control read.`,
      explanation: `${controlFighter}'s control path is to hide entries behind strikes, force defensive reactions, and chain the second effort after the first sprawl or frame. ${controlOpponent} needs first-layer defense and quick exits.`,
    }, used);
  }

  if (id === "method") {
    return finalizeCard({
      ...base,
      targetFighter: winner,
      opponentFighter: opponent,
      read: `${winner} has the best broad method texture, but this model is still weak.`,
      explanation: `Use this card only as a caution label around method language. It helps describe possible finish/decision texture, but it should not be treated as a strong standalone prediction.`,
    }, used);
  }

  if (id === "market") {
    return finalizeCard({
      ...base,
      targetFighter: null,
      opponentFighter: null,
      read: "Market comparison is not active yet.",
      explanation: "FightScope is still reviewing whether odds snapshots are timestamp-safe and fighter-mappable. Until that review passes, market data stays out of the score and out of public betting reads.",
      evidence: ["Odds timing audit is still in review", "No sportsbook lines are shown", "No market edge is calculated"],
      limitations: ["Market model is blocked until timestamp quality and mapping pass review"],
    }, false);
  }

  return finalizeCard({
    ...base,
    read: `${winner} is the stronger contextual read for this signal.`,
    explanation: "This card is supporting context, not a standalone forecast.",
  }, used);
}

export function formatSignalValue(value) {
  if (typeof value === "number") {
    if (Math.abs(value) <= 1) return `${Math.round(value * 100)}%`;
    return value.toFixed(2);
  }
  return value === null || value === undefined ? null : String(value);
}

function finalizeCard(card, used) {
  const caution = reliabilityCaution(card.status, used);
  return {
    ...card,
    caution,
  };
}

function numericConfidence(value) {
  if (typeof value !== "number" || Number.isNaN(value)) return null;
  return value > 1 ? Math.min(value / 100, 1) : Math.max(0, Math.min(value, 1));
}

function confidenceText(value, status) {
  const label = modelStatusLabel(status);
  if (value === null) return label;
  if (value >= 0.72) return `Higher confidence, ${label.toLowerCase()}`;
  if (value >= 0.58) return `Moderate confidence, ${label.toLowerCase()}`;
  return `Thin confidence, ${label.toLowerCase()}`;
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

function fighterStats(latest, prediction) {
  const comparison = latest?.comparison || latest?.result?.comparison || prediction?.comparison || {};
  return {
    a: comparison.stats1 || latest?.fighterA || {},
    b: comparison.stats2 || latest?.fighterB || {},
  };
}

function sameName(a, b) {
  return String(a || "").trim().toLowerCase() === String(b || "").trim().toLowerCase();
}

function pickHigherStat(statsA, statsB, keys, names, fallback) {
  for (const key of keys) {
    const a = numberFromStat(statsA?.[key]);
    const b = numberFromStat(statsB?.[key]);
    if (a !== null && b !== null && a !== b) return a > b ? names.a : names.b;
  }
  return fallback || names.a;
}

function numberFromStat(value) {
  if (typeof value === "number" && Number.isFinite(value)) return value;
  if (typeof value !== "string") return null;
  const parsed = Number(value.replace("%", "").trim());
  return Number.isFinite(parsed) ? parsed : null;
}

function evidenceFor({ id, latest, prediction, signal, model, used, names, stats, confidenceScore }) {
  const evidence = [];
  const status = modelStatusLabel(model.production_status || model.status || signal.status || signal.model_status);
  if (status && status !== "Not reported") evidence.push(`Readiness: ${status}`);
  if (used) evidence.push("Included in the current matchup score");
  if (confidenceScore !== null) evidence.push(`Matchup confidence: ${Math.round(confidenceScore * 100)}%`);
  if (latest?.weightClassDisplay) evidence.push(latest.weightClassDisplay);
  if (prediction?.data_quality || latest?.dataQuality) evidence.push(`Data quality: ${prediction?.data_quality || latest?.dataQuality}`);
  if (id === "strike_volume") {
    addStatEvidence(evidence, names.a, stats.a, ["SLpM", "Sig. Str. LPM"]);
    addStatEvidence(evidence, names.b, stats.b, ["SLpM", "Sig. Str. LPM"]);
  }
  if (id === "takedown_control") {
    addStatEvidence(evidence, names.a, stats.a, ["TD Avg.", "td_avg"]);
    addStatEvidence(evidence, names.b, stats.b, ["TD Avg.", "td_avg"]);
  }
  if (Array.isArray(model.failed_gates) && model.failed_gates.length > 0) {
    evidence.push("Some production gates still need review");
  }
  return evidence.slice(0, 5);
}

function addStatEvidence(evidence, name, stats, keys) {
  for (const key of keys) {
    const value = stats?.[key];
    if (value !== undefined && value !== null && value !== "") {
      evidence.push(`${name} ${key}: ${value}`);
      return;
    }
  }
}

function missingDataList(signal, model, status) {
  const missing = [];
  if (Array.isArray(signal.missing_features)) missing.push(...signal.missing_features);
  if (Array.isArray(model.missing_runtime_features)) missing.push(...model.missing_runtime_features);
  if (String(status || "").toLowerCase() === "not_reported") missing.push("No signal was returned for this matchup");
  return [...new Set(missing)].slice(0, 6);
}

function limitationsFor(status, model) {
  const limitations = [];
  if (Array.isArray(model.limitations)) limitations.push(...model.limitations);
  const value = String(status || "").toLowerCase();
  if (value === BASELINE_REVIEW_STATUS) limitations.push("This model has not beaten the review baseline strongly enough for public-style claims.");
  if (value === "experimental") limitations.push("Use as style context only; do not treat it as a strong numeric forecast.");
  if (value === "high_confidence_only") limitations.push("Use only when the matchup has enough signal quality; weaker segments are still being reviewed.");
  if (value === INACTIVE_STATUS) limitations.push("This model is intentionally off until required data checks pass.");
  return [...new Set(limitations)].slice(0, 4);
}

function dataQualityText(latest, prediction, model) {
  return (
    prediction?.data_quality ||
    latest?.dataQuality ||
    model.data_quality ||
    model.leakage_risk && `Leakage risk: ${model.leakage_risk}` ||
    "Matchup data varies by fighter history and available fields"
  );
}

function reliabilityCaution(status, used) {
  const label = modelStatusLabel(status).toLowerCase();
  if (used) return `Use as a ${label} supporting signal, not a standalone promise.`;
  if (label.includes("experimental")) return "Use as scenario context only until validation is stronger.";
  if (label.includes("weak")) return "Shown for transparency, but it should not drive the read.";
  if (label.includes("blocked") || label.includes("not")) return "Unavailable signals stay out of the score.";
  return `Reliability: ${label}.`;
}
