"""Quick wrapper for the current regime suite."""
from __future__ import annotations

from run_current_regime_suite import run_suite


def main() -> None:
    result = run_suite()
    print(f"Current regime final verdict: {result['overall_verdict']}")


if __name__ == "__main__":
    main()