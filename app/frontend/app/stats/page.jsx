"use client";

import { useLatestPrediction } from "../../lib/latestPrediction";

const STAT_ROWS = [
  ["Record", "Record"],
  ["Weight Class", "Weight Class"],
  ["Elo", "Elo"],
  ["Peak Elo", "Peak Elo"],
  ["Fights counted", "Elo Fights"],
  ["Elo status", "Elo Source"],
  ["Stance", "Stance"],
  ["Height", "Height (cm)"],
  ["Reach", "Reach (cm)"],
  ["SLpM", "SLpM"],
  ["SApM", "SApM"],
  ["TD Avg", "TD Avg"],
  ["TD Def", "TD Def %"],
];

export default function StatsPage() {
  const result = useLatestPrediction();

  if (!result) {
    return (
      <main className="app-shell">
        <section className="panel empty-page">
          <p className="eyebrow">Matchup stats</p>
          <h1>Stats</h1>
          <p>No prediction yet. Generate a matchup on Home first.</p>
          <a className="analysis-link" href="/">Go to Home</a>
        </section>
      </main>
    );
  }

  const statsA = result.comparison?.stats1 || {};
  const statsB = result.comparison?.stats2 || {};
  const matchupType = result.analysis?.matchup_type;

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Expanded matchup stats</p>
          <h1>{statsA.Name} vs {statsB.Name}</h1>
          <div className="matchup-strip">
            <span>{value(statsA, "Weight Class")} vs {value(statsB, "Weight Class")}</span>
            {matchupType && <b className={`matchup-mini-badge ${matchupType.severity}`}>{compactMatchupLabel(matchupType)}</b>}
          </div>
        </div>
      </header>

      <section className="fighter-card-grid">
        <FighterStatCard stats={statsA} label="Fighter A" />
        <FighterStatCard stats={statsB} label="Fighter B" />
      </section>

      <section className="panel stats-grid">
        <h2>{statsA.Name}</h2>
        <h2>{statsB.Name}</h2>
        {STAT_ROWS.map(([label, key]) => (
          <div className="stat-row" key={label}>
            <span>{value(statsA, key)}</span>
            <b>{label}</b>
            <span>{value(statsB, key)}</span>
          </div>
        ))}
      </section>

      <section className="panel empty-page">
        <p className="eyebrow">Data note</p>
        <p>{result.analysis?.data_quality_label || "Unknown"} data quality. Missing fields are shown as "Not available" and are not estimated.</p>
      </section>
    </main>
  );
}

function FighterStatCard({ stats, label }) {
  return (
    <article className="analysis-detail">
      <span>{label}</span>
      <h2>{stats.Name || "Not available"}</h2>
      <p>{value(stats, "Record")} - {value(stats, "Weight Class")}</p>
      <div className="simple-table">
        <div><span>Elo</span><b>{value(stats, "Elo")}</b></div>
        <div><span>Peak Elo</span><b>{value(stats, "Peak Elo")}</b></div>
        <div><span>Fights counted</span><b>{value(stats, "Elo Fights")}</b></div>
        <div><span>Elo status</span><b>{eloStatus(stats)}</b></div>
        <div><span>Stance</span><b>{value(stats, "Stance")}</b></div>
      </div>
    </article>
  );
}

function value(stats, key) {
  if (key === "Elo" && stats?.["Elo Available"] === false) return "Not available";
  if (key === "Elo Source") return eloStatus(stats);
  const raw = stats?.[key];
  return raw === null || raw === undefined || raw === "" || raw === "N/A" ? "Not available" : raw;
}

function eloStatus(stats) {
  const source = String(stats?.["Elo Source"] || "").toLowerCase();
  const fights = Number(stats?.["Elo Fights"] || 0);
  if (!fights || source === "baseline") return "baseline";
  if (fights < 3) return "limited";
  return "computed";
}

function compactMatchupLabel(matchupType) {
  if (matchupType.label === "Same-division matchup") return "Same division";
  if (matchupType.label === "Potential cross-division matchup") return "Possibly cross-division";
  if (matchupType.label === "Cross-division matchup") return "Cross-division";
  return "Weight class unknown";
}
