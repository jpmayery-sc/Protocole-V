"""Quick wrapper for the opening protocol suite."""
from __future__ import annotations

from run_opening_protocol_suite import run_suite


def main() -> None:
    result = run_suite()
    print(f"Opening protocol final verdict: {result['overall_verdict']}")


if __name__ == "__main__":
    main()