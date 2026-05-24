"""Best-effort web scraping agent with file and SQLite cache hooks."""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote_plus

from ufc_predictor.config import settings
from ufc_predictor.db.repository import get_scrape_cache, save_scrape_cache
from ufc_predictor.utils.helpers import normalize_name


def _cache_path(name: str) -> Path:
    settings.SCRAPE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return settings.SCRAPE_CACHE_DIR / f"{normalize_name(name).replace(' ', '_')}.json"


def _read_file_cache(name: str) -> dict | None:
    path = _cache_path(name)
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _write_file_cache(name: str, payload: dict) -> None:
    with open(_cache_path(name), "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def search_fighter_urls(name: str) -> list[dict]:
    quoted = quote_plus(name)
    return [
        {"source": "ufcstats", "url": f"http://ufcstats.com/statistics/fighters/search?query={quoted}", "name": name},
        {"source": "tapology", "url": f"https://www.tapology.com/search?term={quoted}"},
        {"source": "wikipedia", "url": f"https://en.wikipedia.org/wiki/{quote_plus(name).replace('+', '_')}"},
    ]


def scrape_profile(url_info: dict) -> dict:
    try:
        import httpx
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError("Install httpx and beautifulsoup4 to enable scraping") from exc

    url = url_info["url"]
    if url_info.get("source") == "ufcstats":
        profile = _scrape_ufcstats_profile(url_info)
        if profile:
            return profile

    response = httpx.get(url, timeout=15, follow_redirects=True)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text(" ", strip=True)
    title = soup.title.get_text(" ", strip=True) if soup.title else ""
    return {
        "source": url_info.get("source"),
        "url": url,
        "title": title,
        "name": _guess_name_from_title(title),
        "raw_text": text[:5000],
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _scrape_ufcstats_profile(url_info: dict) -> dict | None:
    import httpx
    from bs4 import BeautifulSoup

    name = url_info.get("name") or ""
    search_url = url_info["url"]
    response = httpx.get(search_url, timeout=15, follow_redirects=True)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    profile_url = _pick_ufcstats_profile_url(soup, name)
    if not profile_url:
        return None

    profile_response = httpx.get(profile_url, timeout=15, follow_redirects=True)
    profile_response.raise_for_status()
    profile_soup = BeautifulSoup(profile_response.text, "html.parser")
    text = profile_soup.get_text(" ", strip=True)
    stats = _parse_ufcstats_text(text)
    header = profile_soup.select_one(".b-content__title-highlight")
    stats.update(
        {
            "source": "ufcstats",
            "url": profile_url,
            "name": header.get_text(" ", strip=True) if header else name,
            "raw_text": text[:5000],
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return stats


def _pick_ufcstats_profile_url(soup, name: str) -> str | None:
    query = normalize_name(name)
    best = None
    best_score = 0
    for row in soup.select("tr.b-statistics__table-row"):
        link = row.select_one("a.b-link_style_black")
        if not link or not link.get("href"):
            continue
        row_name = normalize_name(row.get_text(" ", strip=True))
        if query and query in row_name:
            return link["href"]
        score = _simple_overlap_score(query, row_name)
        if score > best_score:
            best = link["href"]
            best_score = score
    return best if best_score >= 0.5 else None


def _parse_ufcstats_text(text: str) -> dict:
    record = {}
    patterns = {
        "height_cm": r"HEIGHT:\s*([0-9'\"]+|--)",
        "weight_in_kg": r"WEIGHT:\s*([0-9]+)\s*lbs\.",
        "reach_in_cm": r"REACH:\s*([0-9]+)",
        "stance": r"STANCE:\s*([A-Za-z ]+?)\s+DOB:",
        "date_of_birth": r"DOB:\s*([A-Za-z]+\s+\d{1,2},\s+\d{4}|--)",
        "slpm": r"SLpM:\s*([0-9.]+)",
        "str_acc": r"Str\. Acc\.:\s*([0-9]+)%",
        "sapm": r"SApM:\s*([0-9.]+)",
        "str_def": r"Str\. Def:\s*([0-9]+)%",
        "td_avg": r"TD Avg\.:\s*([0-9.]+)",
        "td_acc": r"TD Acc\.:\s*([0-9]+)%",
        "td_def": r"TD Def\.:\s*([0-9]+)%",
        "sub_avg": r"Sub\. Avg\.:\s*([0-9.]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            record[key] = match.group(1).strip()

    record_match = re.search(r"Record:\s*(\d+)-(\d+)-(\d+)", text)
    if record_match:
        record["wins"], record["losses"], record["draws"] = record_match.groups()
    if "height_cm" in record:
        record["height_cm"] = _height_to_cm(record["height_cm"])
    if "weight_in_kg" in record:
        record["weight_in_kg"] = round(float(record["weight_in_kg"]) * 0.453592, 2)
    if "reach_in_cm" in record:
        record["reach_in_cm"] = round(float(record["reach_in_cm"]) * 2.54, 2)
    if record.get("date_of_birth") == "--":
        record["date_of_birth"] = None
    return record


def _height_to_cm(value: str) -> float:
    if value == "--":
        return 0.0
    match = re.match(r"(\d+)'\s*(\d+)\"", value)
    if not match:
        return 0.0
    feet, inches = map(float, match.groups())
    return round((feet * 12 + inches) * 2.54, 2)


def _simple_overlap_score(query: str, candidate: str) -> float:
    if not query or not candidate:
        return 0.0
    q = set(query.split())
    c = set(candidate.split())
    return len(q & c) / max(1, len(q))


def scrape_fighter(name: str) -> dict | None:
    normalized = normalize_name(name)
    cached = get_scrape_cache(normalized) or _read_file_cache(name)
    if cached:
        return cached.get("raw", cached)

    last_error = None
    for url_info in search_fighter_urls(name):
        try:
            raw = scrape_profile(url_info)
            raw["name"] = raw.get("name") or name
            save_scrape_cache(normalized, raw.get("source"), raw.get("url"), raw, 0.5)
            _write_file_cache(name, raw)
            return raw
        except Exception as exc:
            last_error = str(exc)
            continue
    return {"source": "manual_placeholder", "name": name, "error": last_error}


def _guess_name_from_title(title: str) -> str | None:
    if not title:
        return None
    clean = re.split(r"[\-|:]", title)[0].strip()
    return clean or None
