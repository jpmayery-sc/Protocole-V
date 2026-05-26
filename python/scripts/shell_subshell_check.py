"""Validate that shells and sub-shells create local breaks inside a period.

The script uses period-2 reference values to check that the broad trends
remain ordered while local dips still appear where sub-shell filling changes.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {"name": "Li", "atomic_radius_pm": 152, "first_ie_ev": 5.39},
    {"name": "Be", "atomic_radius_pm": 112, "first_ie_ev": 9.32},
    {"name": "B", "atomic_radius_pm": 85, "first_ie_ev": 8.30},
    {"name": "C", "atomic_radius_pm": 70, "first_ie_ev": 11.26},
    {"name": "N", "atomic_radius_pm": 65, "first_ie_ev": 14.53},
    {"name": "O", "atomic_radius_pm": 60, "first_ie_ev": 13.62},
    {"name": "F", "atomic_radius_pm": 50, "first_ie_ev": 17.42},
    {"name": "Ne", "atomic_radius_pm": 38, "first_ie_ev": 21.56},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    return {**case}


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    radii = [case["atomic_radius_pm"] for case in evaluated]
    ies = [case["first_ie_ev"] for case in evaluated]

    radius_global_ok = radii[0] > radii[-1] and all(earlier >= later for earlier, later in zip(radii, radii[1:]))
    increasing_steps = sum(1 for earlier, later in zip(ies, ies[1:]) if later > earlier)
    decreasing_steps = sum(1 for earlier, later in zip(ies, ies[1:]) if later < earlier)
    ie_global_ok = ies[0] < ies[-1] and increasing_steps >= decreasing_steps + 1
    b_dip_ok = ies[2] < ies[1]
    o_dip_ok = ies[5] < ies[4]
    local_breaks_ok = b_dip_ok and o_dip_ok

    verdict = "supported" if radius_global_ok and ie_global_ok and local_breaks_ok else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "radius_global_ok": radius_global_ok,
        "ie_global_ok": ie_global_ok,
        "local_breaks_ok": local_breaks_ok,
        "increasing_steps": increasing_steps,
        "decreasing_steps": decreasing_steps,
        "b_dip_ok": b_dip_ok,
        "o_dip_ok": o_dip_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"shell_subshell_check_{ts}.json"
    report_path = outdir / f"shell_subshell_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Shell / sub-shell check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        f"radius_global_ok: {radius_global_ok}",
        f"ie_global_ok: {ie_global_ok}",
        f"local_breaks_ok: {local_breaks_ok}",
        f"increasing_steps: {increasing_steps}",
        f"decreasing_steps: {decreasing_steps}",
        f"b_dip_ok: {b_dip_ok}",
        f"o_dip_ok: {o_dip_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: radius_pm={case['atomic_radius_pm']} first_ie_ev={case['first_ie_ev']}"
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