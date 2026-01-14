"""CLI entrypoint for dataset building."""

from __future__ import annotations

import argparse

from universal_embedding.config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build dataset")
    parser.add_argument("--config", required=True, help="Path to config file")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_result = load_config(args.config)
    print(
        f"Dataset build stub using config: {args.config} "
        f"(merged from {len(config_result.sources)} file(s))"
    )


if __name__ == "__main__":
    main()
