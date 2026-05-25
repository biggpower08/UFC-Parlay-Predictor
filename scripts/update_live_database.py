"""One-command live database refresh for Supabase production data."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.import_supabase import import_all


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply-schema", action="store_true")
    args = parser.parse_args()

    result = import_all(apply_schema_first=args.apply_schema)
    print("Live database update complete:")
    for table, count in result.items():
        print(f"  {table}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
