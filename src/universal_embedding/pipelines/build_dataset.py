"""CLI entrypoint for dataset building."""

from __future__ import annotations

import argparse


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build dataset")
    parser.add_argument("--config", required=True, help="Path to config file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    print(f"Dataset build stub using config: {args.config}")


if __name__ == "__main__":
    main()
