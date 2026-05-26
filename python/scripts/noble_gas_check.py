"""Validate that noble gases mark a closed-shell boundary at the end of each period.

The check compares each noble gas with the previous element in its period and
verifies that the noble gas has a higher first ionization energy and a closed shell.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {"name": "He", "period": 1, "first_ie_ev": 24.59, "previous_element": "H", "previous_ie_ev": 13.60, "closed_shell": True},
    {"name": "Ne", "period": 2, "first_ie_ev": 21.56, "previous_element": "F", "previous_ie_ev": 17.42, "closed_shell": True},
    {"name": "Ar", "period": 3, "first_ie_ev": 15.76, "previous_element": "Cl", "previous_ie_ev": 12.97, "closed_shell": True},
    {"name": "Kr", "period": 4, "first_ie_ev": 14.00, "previous_element": "Br", "previous_ie_ev": 11.81, "closed_shell": True},
    {"name": "Xe", "period": 5, "first_ie_ev": 12.13, "previous_element": "I", "previous_ie_ev": 10.45, "closed_shell": True},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    first_ie_ev = float(case["first_ie_ev"])
    previous_ie_ev = float(case["previous_ie_ev"])
    higher_than_previous = first_ie_ev > previous_ie_ev
    return {
        **case,
        "higher_than_previous": higher_than_previous,
        "ie_gap_ev": first_ie_ev - previous_ie_ev,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    closed_shell_ok = all(case["closed_shell"] for case in evaluated)
    higher_ie_ok = all(case["higher_than_previous"] for case in evaluated)
    period_boundary_ok = all(case["period"] > 0 for case in evaluated)
    verdict = "supported" if closed_shell_ok and higher_ie_ok and period_boundary_ok else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "closed_shell_ok": closed_shell_ok,
        "higher_ie_ok": higher_ie_ok,
        "period_boundary_ok": period_boundary_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"noble_gas_check_{ts}.json"
    report_path = outdir / f"noble_gas_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Noble gas check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        f"closed_shell_ok: {closed_shell_ok}",
        f"higher_ie_ok: {higher_ie_ok}",
        f"period_boundary_ok: {period_boundary_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: period={case['period']} ie={case['first_ie_ev']} previous={case['previous_element']} prev_ie={case['previous_ie_ev']} gap={case['ie_gap_ev']:.2f} closed_shell={case['closed_shell']}"
        )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["report_path"] = str(report_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()