"""Master fighter table, stat extraction, and comparison logic."""

import pandas as pd

from ufc_predictor.config import settings
from ufc_predictor.data_sources.fights import load_fights
from ufc_predictor.db import repository
from ufc_predictor.data_sources.rankings import division_point_dominance, p4p_rankings
from ufc_predictor.models.elo.elo_engine import compute_elo_ratings, get_fighter_elo
from ufc_predictor.utils.helpers import (
    find_name_column,
    get_stat,
    normalize_name,
    safe_float,
)
from ufc_predictor.utils.weight_classes import detect_weight_class

_elo_cache = None
_master_cache = None


def load_stats_df() -> pd.DataFrame:
    df = repository.get_fighters_df()
    name_col = find_name_column(df)
    df["_search_name"] = df[name_col].astype(str).map(normalize_name)
    if "normalized_name" not in df.columns:
        df["normalized_name"] = df["_search_name"]
    return df


def get_elo_tables():
    global _elo_cache
    if _elo_cache is not None:
        return _elo_cache
    fights = load_fights()
    fights_elo, elo_ratings, peak_elo, elo_by_search = compute_elo_ratings(fights)
    _elo_cache = {
        "fights_elo": fights_elo,
        "elo_ratings": elo_ratings,
        "peak_elo": peak_elo,
        "elo_by_search": elo_by_search,
    }
    return _elo_cache


def _rankings_to_search_df(rankings_df, prefix):
    out = rankings_df.copy()
    out["_search_name"] = out["Fighter"].astype(str).map(normalize_name)
    rename = {
        "Rank": f"rank_{prefix}",
        "Points": f"points_{prefix}",
        "Division": f"division_{prefix}",
        "Record": f"record_{prefix}",
    }
    if "Country" in out.columns:
        rename["Country"] = f"country_{prefix}"
    out = out.rename(columns={k: v for k, v in rename.items() if k in out.columns})
    keep = ["_search_name"] + [v for v in rename.values() if v in out.columns]
    return out[keep].drop_duplicates(subset="_search_name", keep="first")


def build_master_df(force_refresh=False):
    global _master_cache
    if _master_cache is not None and not force_refresh:
        return _master_cache.copy()

    stats = load_stats_df()
    name_col = find_name_column(stats)
    master = stats

    if settings.USE_RANKINGS:
        ranking_cols = [
            c
            for c in master.columns
            if c.startswith(("rank_", "points_", "division_", "record_", "country_"))
        ]
        if ranking_cols:
            master = master.drop(columns=ranking_cols)
        p4p = _rankings_to_search_df(p4p_rankings(), "p4p")
        dom = _rankings_to_search_df(division_point_dominance(), "dom")
        master = master.merge(p4p, on="_search_name", how="left")
        master = master.merge(dom, on="_search_name", how="left")

    elo_data = get_elo_tables()
    elo_by_search = elo_data["elo_by_search"]
    peak = elo_data["peak_elo"]
    master["elo"] = master["_search_name"].map(elo_by_search).fillna(settings.ELO_INITIAL)
    master["peak_elo"] = master[name_col].map(
        lambda n: peak.get(n, elo_by_search.get(normalize_name(n), settings.ELO_INITIAL))
    )

    _master_cache = master
    repository.save_fighters_df(master, replace=True)
    return master.copy()


def get_elo_for_row(fighter_row):
    elo_data = get_elo_tables()
    name_col = find_name_column(fighter_row.to_frame().T)
    return get_fighter_elo(fighter_row[name_col], elo_data["elo_by_search"])


def search_fighter(df, name):
    query = normalize_name(name)
    if not query:
        return df.iloc[0:0]
    return df.loc[df["_search_name"] == query].copy()


def extract_stats(fighter_row):
    name_col = find_name_column(fighter_row.to_frame().T)
    name = fighter_row.get(name_col, "Unknown")
    elo = safe_float(fighter_row.get("elo", get_elo_for_row(fighter_row)), settings.ELO_INITIAL)

    return {
        "Name": name,
        "Record": _format_record(fighter_row),
        "Elo": round(elo, 1),
        "Peak Elo": round(safe_float(fighter_row.get("peak_elo"), elo), 1),
        "P4P Rank": _fmt_optional(fighter_row.get("rank_p4p")),
        "P4P Points": _fmt_optional(fighter_row.get("points_p4p")),
        "Dom Rank": _fmt_optional(fighter_row.get("rank_dom")),
        "Dom Points": _fmt_optional(fighter_row.get("points_dom")),
        "SLpM": safe_float(get_stat(fighter_row, "significant_strikes_landed_per_minute", "slpm")),
        "Str Acc %": safe_float(get_stat(fighter_row, "significant_striking_accuracy", "stracc")),
        "SApM": safe_float(get_stat(fighter_row, "significant_strikes_absorbed_per_minute", "sapm")),
        "Str Def %": safe_float(get_stat(fighter_row, "significant_strike_defence", "strdef")),
        "TD Avg": safe_float(get_stat(fighter_row, "average_takedowns_landed_per_15_minutes", "tdavg")),
        "TD Acc %": safe_float(get_stat(fighter_row, "takedown_accuracy", "tdacc")),
        "TD Def %": safe_float(get_stat(fighter_row, "takedown_defense", "tddef")),
        "Sub Avg": safe_float(
            get_stat(fighter_row, "average_submissions_attempted_per_15_minutes", "subavg")
        ),
        "Reach (cm)": safe_float(get_stat(fighter_row, "reach_in_cm", "reach")),
        "Height (cm)": safe_float(get_stat(fighter_row, "height_cm", "height")),
        "Weight (kg)": safe_float(get_stat(fighter_row, "weight_in_kg", "weight")),
        "Weight Class": detect_weight_class(fighter_row),
        "Stance": get_stat(fighter_row, "stance") or "N/A",
    }


def _fmt_optional(val):
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return "N/A"
    if isinstance(val, float) and val == int(val):
        return str(int(val))
    return str(val)


def _format_record(row):
    w, l, d = get_stat(row, "wins", "win"), get_stat(row, "losses", "loss"), get_stat(row, "draws", "draw")
    if w is None and l is None:
        rec = row.get("record_p4p") or row.get("record_dom")
        return str(rec) if rec is not None and not pd.isna(rec) else "N/A"
    parts = [f"{safe_float(w, 0):.0f}W", f"{safe_float(l, 0):.0f}L"]
    if d is not None and safe_float(d) > 0:
        parts.append(f"{safe_float(d):.0f}D")
    return "-".join(parts)


def analyze_style(fighter_row):
    slpm = safe_float(get_stat(fighter_row, "significant_strikes_landed_per_minute", "slpm"), 0)
    str_def = safe_float(get_stat(fighter_row, "significant_strike_defence", "strdef"), 0)
    str_acc = safe_float(get_stat(fighter_row, "significant_striking_accuracy", "stracc"), 0)
    td_avg = safe_float(get_stat(fighter_row, "average_takedowns_landed_per_15_minutes", "tdavg"), 0)
    td_acc = safe_float(get_stat(fighter_row, "takedown_accuracy", "tdacc"), 0)
    td_def = safe_float(get_stat(fighter_row, "takedown_defense", "tddef"), 0)
    sub_avg = safe_float(
        get_stat(fighter_row, "average_submissions_attempted_per_15_minutes", "subavg"), 0
    )
    reach = safe_float(get_stat(fighter_row, "reach_in_cm", "reach"), 0)
    strike_score = slpm * 2.0 + str_def * 0.05 + str_acc * 0.03 + reach * 0.01
    grapple_score = td_avg * 3.0 + sub_avg * 2.0 + td_acc * 0.05 + td_def * 0.02
    if strike_score > grapple_score * 1.25:
        label = "striker-leaning"
    elif grapple_score > strike_score * 1.25:
        label = "grappler-leaning"
    else:
        label = "balanced"
    return {
        "label": label,
        "strike_score": round(strike_score, 2),
        "grapple_score": round(grapple_score, 2),
    }


def compare_fighters(f1, f2):
    stats1, stats2 = extract_stats(f1), extract_stats(f2)
    style1, style2 = analyze_style(f1), analyze_style(f2)
    name1, name2 = stats1["Name"], stats2["Name"]
    numeric_keys = ["Elo", "SLpM", "Str Def %", "TD Avg", "Sub Avg", "Reach (cm)"]
    edges = {
        k: (name1 if stats1[k] > stats2[k] else name2 if stats2[k] > stats1[k] else "even")
        for k in numeric_keys
    }
    s1, w1 = _strengths_weaknesses(stats1, stats2, style1)
    s2, w2 = _strengths_weaknesses(stats2, stats1, style2)
    return {
        "stats1": stats1,
        "stats2": stats2,
        "style1": style1,
        "style2": style2,
        "edges": edges,
        "strengths1": s1,
        "weaknesses1": w1,
        "strengths2": s2,
        "weaknesses2": w2,
        "matchup": _matchup_text(name1, name2, style1, style2, stats1, stats2),
    }


def _strengths_weaknesses(stats_self, stats_opp, style_self):
    strengths, weaknesses = [], []
    if stats_self["Elo"] > stats_opp["Elo"] + 25:
        strengths.append(f"Higher Elo ({stats_self['Elo']} vs {stats_opp['Elo']})")
    elif stats_self["Elo"] < stats_opp["Elo"] - 25:
        weaknesses.append(f"Lower Elo ({stats_self['Elo']} vs {stats_opp['Elo']})")
    if stats_self["SLpM"] >= stats_opp["SLpM"] * 1.1:
        strengths.append("Higher SLpM")
    elif stats_self["SLpM"] < stats_opp["SLpM"] * 0.9:
        weaknesses.append("Lower striking volume")
    if not strengths:
        strengths.append("Competitive on paper")
    if not weaknesses:
        weaknesses.append("No major statistical red flag")
    return strengths, weaknesses


def _matchup_text(name1, name2, style1, style2, stats1, stats2):
    return (
        f"{name1} ({style1['label']}, Elo {stats1['Elo']}) vs "
        f"{name2} ({style2['label']}, Elo {stats2['Elo']})."
    )
