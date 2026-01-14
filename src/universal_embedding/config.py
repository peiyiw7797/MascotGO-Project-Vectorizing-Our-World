"""Configuration loading with include support."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ConfigResult:
    data: dict[str, Any]
    sources: list[Path]


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)
    for key, value in overlay.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"Config file must be a mapping: {path}")
    return data


def _find_repo_root(start: Path) -> Path | None:
    for parent in [start, *start.parents]:
        if (parent / "pyproject.toml").exists() or (parent / ".git").exists():
            return parent
    return None


def _resolve_config_path(path: Path) -> Path:
    if not path.is_absolute() and not path.exists():
        repo_root = _find_repo_root(Path.cwd())
        if repo_root is not None:
            candidate = repo_root / path
            if candidate.exists():
                return candidate
    return path


def _load_with_includes(path: Path) -> ConfigResult:
    data = _load_yaml(path)
    sources = [path]

    includes = data.pop("includes", [])
    if includes:
        if not isinstance(includes, list):
            raise ValueError("includes must be a list of relative paths")
        merged: dict[str, Any] = {}
        for include in includes:
            include_path = (path.parent / include).resolve()
            include_result = _load_with_includes(include_path)
            merged = _deep_merge(merged, include_result.data)
            sources.extend(include_result.sources)
        data = _deep_merge(merged, data)

    return ConfigResult(data=data, sources=sources)


def load_config(config_path: str | Path) -> ConfigResult:
    path = _resolve_config_path(Path(config_path))
    return _load_with_includes(path)


def load_config_from_files(paths: list[str | Path]) -> ConfigResult:
    merged: dict[str, Any] = {}
    sources: list[Path] = []
    for path in paths:
        resolved = _resolve_config_path(Path(path))
        data = _load_yaml(resolved)
        merged = _deep_merge(merged, data)
        sources.append(resolved)
    return ConfigResult(data=merged, sources=sources)
