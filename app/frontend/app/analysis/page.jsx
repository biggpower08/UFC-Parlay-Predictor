"use client";

import { useEffect, useState } from "react";

export default function AnalysisPage() {
  const [result, setResult] = useState(null);

  useEffect(() => {
    try {
      const saved = localStorage.getItem("latestPredictionResult");
      if (saved) setResult(JSON.parse(saved));
    } catch {
      setResult(null);
    }
  }, []);

  if (!result) {
    return (
      <main className="app-shell">
        <section className="panel empty-page">
          <p className="eyebrow">Analysis</p>
          <h1>Fight Analysis</h1>
          <p>Choose two fighters on the prediction page to generate a full analysis.</p>
          <a className="analysis-link" href="/">Open prediction page</a>
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

      {analysis.sections?.length > 0 && (
        <section className="analysis-page-grid">
          {analysis.sections.map((section, index) => (
            <article className="analysis-detail" key={section.title}>
              <span>{String(index + 1).padStart(2, "0")}</span>
              <h2>{section.title}</h2>
              <p>{section.body}</p>
            </article>
          ))}
        </section>
      )}
    </main>
  );
}
