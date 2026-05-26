"""Quick wrapper for the H / Fe / Pb campaign suite."""
from __future__ import annotations

from run_h_fe_pb_suite import run_suite


def main() -> None:
    result = run_suite()
    print(f"H / Fe / Pb final verdict: {result['overall_verdict']}")


if __name__ == "__main__":
    main()