"use client";

import { useEffect, useState } from "react";
const API_BASE = "/api";

async function fetchJson(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export default function OddsPage() {
  const [status, setStatus] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchJson("/odds/status").then(setStatus).catch((error) => setMessage(`Odds status unavailable: ${error.message}`));
  }, []);

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
          <strong>Market comparison is not active yet</strong>
          <span>{status?.message || "Live market comparison remains inactive while odds mapping and timing checks are completed."}</span>
        </div>
        <p>Independent MMA analytics only. Not affiliated with UFC, any promotion, sportsbook, or betting operator. Outputs are informational and research-oriented, not financial advice.</p>
      </section>

      <section className="odds-simple-grid market-only">
        <article className="panel">
          <p className="eyebrow">Research preview</p>
          <h2>Timestamp-safe moneyline snapshots</h2>
          <p>
            The odds dataset is being reviewed for fighter mapping, event timing, and snapshot safety before market-aware reads can be used.
          </p>
        </article>
        <article className="panel">
          <p className="eyebrow">Safety</p>
          <h2>No active market outputs</h2>
          <p>No wagering actions or market-strength claims are shown. Market comparison stays inactive until review passes.</p>
        </article>
      </section>
    </main>
  );
}
