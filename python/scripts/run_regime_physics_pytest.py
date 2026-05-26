"""Run the pytest regime-physics subsets by marker or the full set."""
from __future__ import annotations

import argparse
from regime_test_runner import run_pytest


MARKER_CHOICES = ("atomique", "metal", "lanthanide", "dense", "flow", "all")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the pytest regime-physics subsets by marker or the full set.")
    parser.add_argument("marker", choices=MARKER_CHOICES, help="Marker to run, or all for the full suite")
    args = parser.parse_args()

    run_pytest(None if args.marker == "all" else args.marker)


if __name__ == "__main__":
    main()