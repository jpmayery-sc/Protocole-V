"""Validate broad periodic trends with local sub-shell breaks across two periods.

The script checks that atomic radius decreases and ionization energy increases
overall across a period, while known local dips remain visible.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


PERIODS = {
    "period2": [
        {"name": "Li", "radius_pm": 152, "ie_ev": 5.39},
        {"name": "Be", "radius_pm": 112, "ie_ev": 9.32},
        {"name": "B", "radius_pm": 85, "ie_ev": 8.30},
        {"name": "C", "radius_pm": 70, "ie_ev": 11.26},
        {"name": "N", "radius_pm": 65, "ie_ev": 14.53},
        {"name": "O", "radius_pm": 60, "ie_ev": 13.62},
        {"name": "F", "radius_pm": 50, "ie_ev": 17.42},
        {"name": "Ne", "radius_pm": 38, "ie_ev": 21.56},
    ],
    "period3": [
        {"name": "Na", "radius_pm": 186, "ie_ev": 5.14},
        {"name": "Mg", "radius_pm": 160, "ie_ev": 7.65},
        {"name": "Al", "radius_pm": 143, "ie_ev": 5.99},
        {"name": "Si", "radius_pm": 118, "ie_ev": 8.15},
        {"name": "P", "radius_pm": 110, "ie_ev": 10.49},
        {"name": "S", "radius_pm": 104, "ie_ev": 10.36},
        {"name": "Cl", "radius_pm": 99, "ie_ev": 12.97},
        {"name": "Ar", "radius_pm": 71, "ie_ev": 15.76},
    ],
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_period(cases: list[dict]) -> dict:
    radii = [case["radius_pm"] for case in cases]
    ies = [case["ie_ev"] for case in cases]
    radius_global_ok = radii[0] > radii[-1] and all(earlier >= later for earlier, later in zip(radii, radii[1:]))
    ie_global_ok = ies[0] < ies[-1] and sum(1 for earlier, later in zip(ies, ies[1:]) if later > earlier) >= sum(
        1 for earlier, later in zip(ies, ies[1:]) if later < earlier
    ) + 1
    dips = [case["name"] for earlier, later, case in zip(ies, ies[1:], cases[1:]) if later < earlier]
    local_breaks_ok = len(dips) >= 2
    return {
        "cases": cases,
        "radius_global_ok": radius_global_ok,
        "ie_global_ok": ie_global_ok,
        "local_breaks_ok": local_breaks_ok,
        "dips": dips,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    period_results = {name: evaluate_period(cases) for name, cases in PERIODS.items()}

    overall_ok = all(result["radius_global_ok"] and result["ie_global_ok"] and result["local_breaks_ok"] for result in period_results.values())
    verdict = "supported" if overall_ok else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "period_results": period_results,
    }

    json_path = outdir / f"period_trend_check_{ts}.json"
    report_path = outdir / f"period_trend_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Period trend check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        "",
    ]
    for period_name, result in period_results.items():
        lines.append(f"{period_name}:")
        lines.append(f"- radius_global_ok: {result['radius_global_ok']}")
        lines.append(f"- ie_global_ok: {result['ie_global_ok']}")
        lines.append(f"- local_breaks_ok: {result['local_breaks_ok']}")
        lines.append(f"- dips: {', '.join(result['dips']) if result['dips'] else 'none'}")
        lines.append("")
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