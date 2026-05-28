"use client";

import { Search } from "lucide-react";
import { useEffect, useState } from "react";

const API_BASE = "/api";

async function fetchJson(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) throw new Error(await response.text());
  return response.json();
}

export default function StatsPage() {
  const [query, setQuery] = useState("");
  const [rankings, setRankings] = useState([]);
  const [fighters, setFighters] = useState([]);
  const [selected, setSelected] = useState(null);
  const [eloHistory, setEloHistory] = useState([]);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchJson("/rankings?limit=12")
      .then((data) => setRankings(data.rankings || []))
      .catch((error) => setMessage(`Rankings unavailable: ${error.message}`));
  }, []);

  async function searchFighters(value) {
    setQuery(value);
    setSelected(null);
    setEloHistory([]);
    if (value.trim().length < 2) {
      setFighters([]);
      return;
    }
    try {
      const data = await fetchJson(`/fighters/search?q=${encodeURIComponent(value)}&limit=8`);
      setFighters(data.fighters || []);
    } catch (error) {
      setMessage(`Search failed: ${error.message}`);
    }
  }

  async function pickFighter(fighter) {
    setSelected(fighter);
    setQuery(fighter.name);
    setFighters([]);
    try {
      const data = await fetchJson(`/fighters/${encodeURIComponent(fighter.name)}/elo-history?limit=30`);
      setEloHistory(data.elo_history || []);
    } catch {
      setEloHistory([]);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Stats lab</p>
          <h1>Fighter Stats</h1>
        </div>
      </header>

      {message && <div className="message"><span>{message}</span></div>}

      <section className="panel stat-search-panel">
        <label className="fighter-input">
          <span>Find a fighter</span>
          <div className="input-wrap">
            <Search size={18} />
            <input value={query} placeholder="Search fighter stats" onChange={(event) => searchFighters(event.target.value)} />
          </div>
          {fighters.length > 0 && (
            <div className="suggestions">
              {fighters.map((fighter) => (
                <button type="button" key={fighter.name} onClick={() => pickFighter(fighter)}>
                  <span>{fighter.name}</span>
                  <small>{fighter.weight_class || "Unknown"}</small>
                </button>
              ))}
            </div>
          )}
        </label>
      </section>

      {selected ? (
        <section className="panel stats-profile">
          <div>
            <p className="eyebrow">Profile</p>
            <h2>{selected.name}</h2>
            <p>{selected.nickname ? `"${selected.nickname}"` : "No nickname listed"}</p>
          </div>
          <div className="ready-grid">
            <div><strong>Weight class</strong><span>{selected.weight_class || "Unknown"}</span></div>
            <div><strong>Record</strong><span>{selected.wins ?? 0}-{selected.losses ?? 0}-{selected.draws ?? 0}</span></div>
            <div><strong>Elo history rows</strong><span>{eloHistory.length}</span></div>
          </div>
          {eloHistory.length > 0 ? (
            <div className="simple-table">
              {eloHistory.slice(0, 8).map((row, index) => (
                <div key={`${row.computed_at}-${index}`}>
                  <span>{row.computed_at || "Computed"}</span>
                  <b>{row.elo}</b>
                </div>
              ))}
            </div>
          ) : (
            <p className="helper-text">No Elo history rows returned for this fighter yet.</p>
          )}
        </section>
      ) : (
        <section className="panel empty-page">
          <p>Search for a fighter to inspect available profile and Elo data. Missing fields are shown as unknown rather than estimated.</p>
        </section>
      )}

      <section className="panel">
        <p className="eyebrow">Current Elo rankings</p>
        <div className="simple-table">
          {rankings.map((row) => (
            <div key={`${row.ranking_type}-${row.rank}-${row.fighter_name}`}>
              <span>{row.rank}. {row.fighter_name}</span>
              <b>{row.elo}</b>
            </div>
          ))}
          {rankings.length === 0 && <p className="helper-text">Rankings are unavailable right now.</p>}
        </div>
      </section>
    </main>
  );
}
