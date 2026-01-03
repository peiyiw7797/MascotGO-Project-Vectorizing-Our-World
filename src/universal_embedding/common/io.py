"""I/O helpers for common formats."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, Mapping


def write_jsonl(path: str | Path, rows: Iterable[Mapping]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row) + "\n")


def write_csv(path: str | Path, rows: Iterable[Mapping], fieldnames: list[str]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
