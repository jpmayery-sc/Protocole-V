"""Quick wrapper for the alpha and orbital suite."""
from __future__ import annotations

from run_alpha_orbitals_suite import run_suite


def main() -> None:
    result = run_suite()
    print(f"Alpha / orbitals final verdict: {result['overall_verdict']}")


if __name__ == "__main__":
    main()