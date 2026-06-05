"""Command-line entry point for the data pipeline."""
from __future__ import annotations

import argparse

COMMANDS: tuple[str, ...] = ("build", "validate")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="busanalytics-pipeline")
    parser.add_argument("command", choices=COMMANDS)
    args = parser.parse_args(argv)
    print(f"pipeline: '{args.command}' not yet implemented (P1)")
    return 0
