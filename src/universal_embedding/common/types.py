"""Shared type definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    seed: int
    persona_count: int
    session_range: tuple[int, int]
