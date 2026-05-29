"""Small on-disk fetch cache."""

from __future__ import annotations

import hashlib
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse


class FetchCache:
    def __init__(self, root: Path) -> None:
        self.root = Path(root)

    def path_for(self, url: str) -> Path:
        parsed = urlparse(url)
        slug = hashlib.sha256(url.encode("utf-8")).hexdigest()
        suffix = Path(parsed.path).name or "index"
        return self.root / f"{suffix}-{slug}.html"

    def read(self, url: str) -> str | None:
        path = self.path_for(url)
        if not path.is_file():
            return None
        return path.read_text(encoding="utf-8")

    def exists(self, url: str) -> bool:
        return self.path_for(url).is_file()

    def age_seconds(self, url: str) -> float | None:
        path = self.path_for(url)
        if not path.is_file():
            return None
        modified = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc)
        return (datetime.now(timezone.utc) - modified).total_seconds()

    def write(self, url: str, text: str) -> None:
        path = self.path_for(url)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
