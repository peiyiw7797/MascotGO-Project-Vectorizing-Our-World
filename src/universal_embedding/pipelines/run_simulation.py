"""CLI entrypoint for simulation runs."""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run simulation")
    parser.add_argument("--config", required=True, help="Path to config file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Simulation stub using config: {args.config}")


if __name__ == "__main__":
    main()
