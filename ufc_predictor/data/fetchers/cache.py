"""Small on-disk fetch cache."""

from __future__ import annotations

import hashlib
from pathlib import Path
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

    def write(self, url: str, text: str) -> None:
        path = self.path_for(url)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
