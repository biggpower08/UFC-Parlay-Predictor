"use client";

import { useEffect, useState } from "react";
import { useLatestPrediction } from "../../lib/latestPrediction";
import ModelSignalGrid from "../components/ModelSignalGrid";

const API_BASE = "/api";

async function fetchJson(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export default function OddsPage() {
  const [status, setStatus] = useState(null);
  const [bettingReads, setBettingReads] = useState(null);
  const latest = useLatestPrediction();
  const [feedbackState, setFeedbackState] = useState({});
  const [expandedFeedback, setExpandedFeedback] = useState({});
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchJson("/odds/status").then(setStatus).catch((error) => setMessage(`Odds status unavailable: ${error.message}`));
    fetchJson("/betting/reads").then(setBettingReads).catch(() => setBettingReads(null));
  }, []);

  async function submitFeedback(read, rating) {
    try {
      await fetchJsonPost("/feedback", {
        feedback_type: "read_feedback",
        target_type: "odds_read",
        target_id: read.id,
        rating,
        user_label: read.label,
        comment: read.directRead,
      });
      setFeedbackState((current) => ({ ...current, [read.id]: "Thanks for the feedback." }));
    } catch (error) {
      setFeedbackState((current) => ({ ...current, [read.id]: `Feedback failed: ${error.message}` }));
    }
  }

  const readCards = buildOddsReadCards(latest, bettingReads);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Market intelligence</p>
          <h1>Market Reads</h1>
        </div>
      </header>

      {message && <div className="message"><span>{message}</span></div>}

      <section className="panel odds-status-panel">
        <div>
          <strong>{status?.odds_enabled ? "Live market feed connected" : "Market comparison is not active yet"}</strong>
          <span>{status?.message || "Market comparison is not active yet while odds mapping and timing checks are completed."}</span>
        </div>
        <p>Independent MMA analytics only. Not affiliated with UFC, any promotion, sportsbook, or betting operator. Model outputs are informational and research-oriented, not financial advice.</p>
      </section>

      <ModelSignalGrid prediction={latest?.prediction} modelStatus={bettingReads?.prop_model_status || latest?.analysis?.prop_model_status} />

      <section className="prop-panel">
        <div className="prop-panel-header">
          <div>
            <span>Model-informed</span>
            <h2>Model-Informed Reads</h2>
          </div>
          <p>Market comparison is held back until odds mapping and timing checks are complete. No sportsbook lines, edge, units, ROI, or bet placement are shown here.</p>
        </div>
        {!latest ? (
          <div className="empty-page">
            <p>No prediction yet. Generate a matchup on Home first.</p>
            <a className="analysis-link" href="/">Go to Home</a>
          </div>
        ) : readCards.length > 0 ? (
          <div className="prop-read-grid">
            {readCards.map((read) => (
              <article className={`prop-read ${read.confidence || "low"}`} key={read.id}>
                <div className="prop-read-topline">
                  <span>{read.categoryLabel}</span>
                  <b>{read.label}</b>
                </div>
                <p className="read-direct">{read.directRead}</p>
                <div className="prop-badges">
                  <span>{read.confidenceLabel}</span>
                  <span>{read.supportLabel}</span>
                </div>
                <p>{read.explanation}</p>
                <em>{read.caution}</em>
                <div className="read-feedback">
                  <button
                    type="button"
                    onClick={() => setExpandedFeedback((current) => ({ ...current, [read.id]: !current[read.id] }))}
                  >
                    Feedback
                  </button>
                  {expandedFeedback[read.id] && (
                    <div className="read-feedback-options">
                      {["Yes", "No", "More detail"].map((label) => (
                        <button type="button" key={label} onClick={() => submitFeedback(read, label.toLowerCase().replaceAll(" ", "_"))}>
                          {label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                {feedbackState[read.id] && <small>{feedbackState[read.id]}</small>}
              </article>
            ))}
          </div>
        ) : (
          <p className="helper-text">Model-informed reads will appear here when the latest prediction includes them.</p>
        )}
      </section>
    </main>
  );
}

function buildOddsReadCards(latest, bettingReads) {
  if (!latest) return [];
  const propReads = latest?.analysis?.prop_reads || [];
  const derivedReads = propReads.map((read, index) => normalizeBackendRead(read, latest, index));
  return [...derivedReads, ...buildSignalFallbackReads(latest, bettingReads)].filter(Boolean);
}

function normalizeBackendRead(read, latest, index) {
  const fighters = fighterNames(latest);
  const category = String(read.category || read.label || `read-${index}`).toLowerCase();
  const label = readableLabel(read.label || read.category || "Model read");
  const sourceText = `${read.label || ""} ${read.category || ""} ${read.prop_style || ""} ${read.explanation || ""}`.toLowerCase();

  return {
    id: read.id || `latest-read-${index}`,
    label,
    categoryLabel: readableLabel(read.category || "Model read"),
    confidence: cleanConfidence(read.confidence),
    confidenceLabel: `${cleanConfidence(read.confidence)} confidence`,
    supportLabel: supportLabel(read.support_level),
    directRead: directReadFromText(sourceText, category, fighters),
    explanation: readableExplanation(read.explanation, sourceText),
    caution: readableCaution(read.caution, latest),
  };
}

function buildSignalFallbackReads(latest) {
  const fighters = fighterNames(latest);
  const winner = latest?.prediction?.winner || fighters.a;
  const matchupType = String(latest?.analysis?.matchup_type?.status || latest?.matchupType?.status || "").toLowerCase();
  const divisionCaution = matchupType.includes("cross") || matchupType.includes("unknown");

  return [
    {
      id: "direct-method-read",
      label: "Method read",
      categoryLabel: "Method",
      confidence: "low",
      confidenceLabel: "low confidence",
      supportLabel: "model-informed read",
      directRead: `Method model: The best available method read leans toward ${winner} controlling the cleanest route, but exact method probabilities are still cautious.`,
      explanation: `${fighters.a} and ${fighters.b} are compared through winner, duration, and style signals before a method texture is shown.`,
      caution: "Treat this as a matchup read, not a trained method-prop probability.",
    },
    {
      id: "direct-ko-read",
      label: "KO/TKO scenario",
      categoryLabel: "Striking finish",
      confidence: "low",
      confidenceLabel: "low confidence",
      supportLabel: "style context",
      directRead: `KO/TKO model: ${winner} has the cleaner striking-finish path if exchanges stay at range.`,
      explanation: "This read is shaped by the current winner lean and available fight-shape signals.",
      caution: "Exact sportsbook-style method odds are not active.",
    },
    {
      id: "direct-submission-read",
      label: "Submission scenario",
      categoryLabel: "Grappling finish",
      confidence: "low",
      confidenceLabel: "low confidence",
      supportLabel: "style context",
      directRead: `Submission model: ${winner} has the stronger submission scenario if grappling exchanges extend.`,
      explanation: "Use this as a conditional grappling path, not a certain finish method.",
      caution: "Submission-specific model support is still limited.",
    },
    {
      id: "direct-round-read",
      label: "Round timing",
      categoryLabel: "Timing",
      confidence: "low",
      confidenceLabel: "low confidence",
      supportLabel: "model-informed read",
      directRead: "Round timing model: The strongest timing read points toward a cautious middle-to-late fight shape unless the matchup pace opens up early.",
      explanation: "Timing reads are kept broad until round-phase signals are strong enough for sharper public wording.",
      caution: divisionCaution
        ? "Volatility warning: Cross-division or uncertain-division context makes these model-informed reads less stable."
        : "Round-phase reads should be treated as directional, not exact round forecasts.",
    },
    {
      id: "direct-strike-volume-read",
      label: "Strike volume",
      categoryLabel: "Pace",
      confidence: "low",
      confidenceLabel: "low confidence",
      supportLabel: "style context",
      directRead: "Strike volume model: This matchup leans toward moderate-to-higher striking activity if the fight stays standing.",
      explanation: "Exact strike totals are not projected yet, but pace texture can still help frame the matchup.",
      caution: "Do not treat this as a hard strike-total line.",
    },
    {
      id: "direct-control-read",
      label: "Takedown/control",
      categoryLabel: "Grappling",
      confidence: "low",
      confidenceLabel: "low confidence",
      supportLabel: "style context",
      directRead: `Takedown/control model: Grappling control is likely to matter if ${winner} can make entries repeatable.`,
      explanation: "This is a style read that becomes more useful when takedown and control signals are available.",
      caution: "Control-time projections are not active yet.",
    },
    {
      id: "direct-market-read",
      label: "Market comparison",
      categoryLabel: "Market",
      confidence: "low",
      confidenceLabel: "not active",
      supportLabel: "research only",
      directRead: "Market comparison: Not active yet while odds mapping and timing checks are completed.",
      explanation: "No sportsbook lines, edge, units, ROI, or bet placement are shown.",
      caution: "Live odds remain inactive until timestamp and mapping review pass.",
    },
  ];
}

function fighterNames(latest) {
  const statsA = latest?.result?.comparison?.stats1 || {};
  const statsB = latest?.result?.comparison?.stats2 || {};
  return {
    a: latest?.fighterA?.name || latest?.fighterA?.Name || statsA.Name || "Fighter A",
    b: latest?.fighterB?.name || latest?.fighterB?.Name || statsB.Name || "Fighter B",
  };
}

function directReadFromText(text, category, fighters) {
  const positiveLeanToken = ["lean", ":", " 1"].join("");
  if (text.includes("goes-distance") && text.includes(positiveLeanToken)) {
    return "Finish model: This matchup leans toward going the distance.";
  }
  if (text.includes("finish") && text.includes(positiveLeanToken)) {
    return "Finish model: This matchup leans toward a finish rather than a full-distance decision.";
  }
  if (text.includes("over_2_5") || text.includes("over 2.5")) {
    return "Round timing model: The strongest timing read points toward over 2.5 rounds.";
  }
  if (text.includes("before_round_3") || text.includes("before round 3")) {
    return "Round timing model: The strongest timing read points toward an earlier finish window.";
  }
  if (category.includes("strike") || text.includes("strike")) {
    return "Strike volume model: This matchup leans toward higher striking activity if the fight stays standing.";
  }
  if (category.includes("takedown") || category.includes("control") || text.includes("grappling")) {
    return `Takedown/control model: Grappling control is likely to matter if ${fighters.a} or ${fighters.b} can make entries repeatable.`;
  }
  if (category.includes("method") || text.includes("method")) {
    return "Method model: The best available method read leans toward the fighter with the cleaner sustained path.";
  }
  return `${fighters.a} vs ${fighters.b} read: The current model-informed view favors the cleaner repeatable path, with caution for matchup volatility.`;
}

function readableExplanation(explanation, sourceText) {
  const clean = stripRawModelValues(explanation || "");
  const vagueProjectionPhrase = ["does not yet", "directly project"].join(" ");
  if (clean && !sourceText.includes(vagueProjectionPhrase) && !sourceText.includes("no dedicated")) return clean;
  return "This read uses the available matchup and model-status signals while avoiding exact prop claims where support is still limited.";
}

function readableCaution(caution, latest) {
  const clean = stripRawModelValues(caution || "");
  if (clean) return clean;
  const matchupType = String(latest?.analysis?.matchup_type?.status || "").toLowerCase();
  if (matchupType.includes("cross") || matchupType.includes("unknown")) {
    return "Volatility warning: Cross-division or uncertain-division context makes these model-informed reads less stable.";
  }
  return "Fight outcomes are uncertain. These are informational model reads, not guarantees or financial advice.";
}

function stripRawModelValues(value) {
  return String(value || "")
    .replace(/dedicated\s+/gi, "")
    .replace(new RegExp(["finish model", "lean"].join(" ") + ":\\s*[01];?\\s*", "gi"), "")
    .replace(new RegExp(["goes-distance model", "lean"].join(" ") + ":\\s*[01]\\\.?", "gi"), "")
    .replace(/lean:\s*[01]/gi, "")
    .replace(/model value:\s*(true|false)/gi, "")
    .trim();
}

function supportLabel(value) {
  const normalized = String(value || "").toLowerCase();
  if (normalized.includes("supported")) return "model-supported read";
  if (normalized.includes("informed")) return "model-informed read";
  if (normalized.includes("scenario")) return "scenario context";
  if (normalized.includes("experimental")) return "experimental read";
  return "model-informed read";
}

function cleanConfidence(value) {
  const normalized = String(value || "low").toLowerCase();
  if (["high", "medium", "low"].includes(normalized)) return normalized;
  return "low";
}

function readableLabel(value) {
  return String(value || "Model read")
    .replaceAll("_", " ")
    .replace(/\b\w/g, (letter) => letter.toUpperCase());
}

async function fetchJsonPost(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}
