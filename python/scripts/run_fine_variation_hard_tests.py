"""Quick wrapper for the fine-variation hard suite."""
from __future__ import annotations

from run_fine_variation_hard_suite import run_suite


def main() -> None:
    result = run_suite()
    print(f"Fine variation hard final verdict: {result['overall_verdict']}")


if __name__ == "__main__":
    main()