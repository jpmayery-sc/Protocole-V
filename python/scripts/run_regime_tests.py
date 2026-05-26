"""Run the regime-physics test wrappers from one command.

Subcommands map to the fixed wrappers so the higher-level entry point stays
simple while the underlying regime checks remain isolated.
"""
from __future__ import annotations

import argparse
from regime_test_runner import run_marker


SUBCOMMANDS = ("atomique", "metal", "lanthanide", "dense", "all")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the regime-physics test wrappers from one command.")
    parser.add_argument("regime", choices=SUBCOMMANDS, help="Regime to run, or all to run every subset")
    args = parser.parse_args()

    if args.regime == "all":
        for name in ("atomique", "metal", "lanthanide", "dense"):
            run_marker(name)
        return

    run_marker(args.regime)


if __name__ == "__main__":
    main()