"use client";

import { useEffect, useState } from "react";
import { loadLatestPrediction } from "../../lib/latestPrediction";

export default function AnalysisPage() {
  const [result, setResult] = useState(null);

  useEffect(() => {
    setResult(loadLatestPrediction());
  }, []);

  if (!result) {
    return (
      <main className="app-shell">
        <section className="panel empty-page">
          <p className="eyebrow">Analysis</p>
          <h1>Fight Analysis</h1>
          <p>Generate a prediction on the Home page to unlock the full analysis.</p>
          <a className="analysis-link" href="/">Go to Home</a>
        </section>
      </main>
    );
  }

  const analysis = result.analysis || {};
  const comparison = result.comparison || {};

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Full fight breakdown</p>
          <h1>{comparison.stats1?.Name} vs {comparison.stats2?.Name}</h1>
        </div>
      </header>

      <section className="panel prediction-panel">
        <div className="analysis-badges">
          <span>{analysis.confidence_label}</span>
          <span>{analysis.volatility_label} volatility</span>
          <span>{analysis.data_quality_label} data</span>
          {analysis.matchup_type && <span className={`matchup-badge ${analysis.matchup_type.severity}`}>{analysis.matchup_type.label}</span>}
        </div>
        <div className="analyst-read">
          <span>Analyst summary</span>
          <p>{analysis.summary || result.summary}</p>
        </div>
        {analysis.warnings?.length > 0 && (
          <div className="analysis-warnings">
            {analysis.warnings.map((warning) => <p key={warning}>{warning}</p>)}
          </div>
        )}
      </section>

      <section className="analysis-page-grid">
          {(analysis.sections?.length ? analysis.sections : fallbackSections()).map((section, index) => (
            <article className="analysis-detail" key={section.title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h2>{section.title}</h2>
              <p>{section.body}</p>
            </article>
          ))}
      </section>
    </main>
  );
}

function fallbackSections() {
  return [
    "Main prediction read",
    "Why the model leans this way",
    "Fighter A path to victory",
    "Fighter B path to victory",
    "Method lean",
    "Round-phase outlook",
    "Key exchanges",
    "Pace/volume read",
    "Swing factors",
    "Volatility warning",
    "Data quality note",
    "Final analyst read",
  ].map((title) => ({
    title,
    body: "This section will expand as more matchup data becomes available.",
  }));
}
