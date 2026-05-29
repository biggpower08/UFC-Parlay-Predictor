"use client";

import { useEffect, useState } from "react";
import { useLatestPrediction } from "../../lib/latestPrediction";

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
        comment: read.prop_style,
      });
      setFeedbackState((current) => ({ ...current, [read.id]: "Thanks for the feedback." }));
    } catch (error) {
      setFeedbackState((current) => ({ ...current, [read.id]: `Feedback failed: ${error.message}` }));
    }
  }

  const propReads = latest?.analysis?.prop_reads || [];

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Infrastructure mode</p>
          <h1>Betting Odds</h1>
        </div>
      </header>

      {message && <div className="message"><span>{message}</span></div>}

      <section className="panel odds-status-panel">
        <div>
          <strong>{status?.odds_enabled ? "Live odds connected" : "Live odds not connected"}</strong>
          <span>{status?.message || "Live sportsbook odds are not connected yet. These are model-informed betting reads, not sportsbook lines."}</span>
        </div>
        <p>These betting reads are informational model analysis only. They are not guarantees or financial advice. Fight outcomes are uncertain.</p>
      </section>

      {bettingReads?.prop_model_status && (
        <section className="panel">
          <p className="eyebrow">Dedicated model status</p>
          <div className="ready-grid">
            {Object.values(bettingReads.prop_model_status).slice(0, 6).map((model) => (
              <div key={model.name}>
                <strong>{model.name.replaceAll("_", " ")}</strong>
                <span>{model.status}</span>
              </div>
            ))}
          </div>
        </section>
      )}

      <section className="prop-panel">
        <div className="prop-panel-header">
          <div>
            <span>Model-informed</span>
            <h2>Betting Reads</h2>
          </div>
          <p>No fake odds, edge, units, ROI, or bet placement is shown here.</p>
        </div>
        {!latest ? (
          <div className="empty-page">
            <p>No prediction yet. Generate a matchup on Home first.</p>
            <a className="analysis-link" href="/">Go to Home</a>
          </div>
        ) : propReads.length > 0 ? (
          <div className="prop-read-grid">
            {propReads.map((read) => (
              <article className={`prop-read ${read.confidence || "low"}`} key={read.id}>
                <div className="prop-read-topline">
                  <span>{read.category?.replaceAll("_", " ") || "read"}</span>
                  <b>{read.label}</b>
                </div>
                <p className="prop-style">{read.prop_style}</p>
                <div className="prop-badges">
                  <span>{read.confidence || "low"} confidence</span>
                  <span>{String(read.support_level || "scenario_read").replaceAll("_", " ")}</span>
                </div>
                <p>{read.explanation}</p>
                <em>{read.caution}</em>
                <div className="read-feedback">
                  {["Helpful", "Not helpful", "Too vague", "Too risky", "Seems wrong", "I want more detail"].map((label) => (
                    <button type="button" key={label} onClick={() => submitFeedback(read, label.toLowerCase().replaceAll(" ", "_"))}>{label}</button>
                  ))}
                </div>
                {feedbackState[read.id] && <small>{feedbackState[read.id]}</small>}
              </article>
            ))}
          </div>
        ) : (
          <p className="helper-text">Prop-style reads will appear here when the latest prediction includes them.</p>
        )}
      </section>
    </main>
  );
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
