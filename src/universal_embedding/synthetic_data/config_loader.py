"""Multimodal config loader for Issue #2 checkpoints."""

from __future__ import annotations

from pathlib import Path

from universal_embedding.config import ConfigResult, load_config, load_config_from_files

DEFAULT_CHECKPOINTS = [
    Path("configs/checkpoints/00_run_paths.yaml"),
    Path("configs/checkpoints/30_multimodal.yaml"),
]


def load_multimodal_config(config_path: str | Path | None = None) -> ConfigResult:
    if config_path is not None:
        return load_config(config_path)
    return load_config_from_files(DEFAULT_CHECKPOINTS)
