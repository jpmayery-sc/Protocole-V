"""Dual-core refinement for the 5d transition-metal block.

This script tests whether the 5d block is best read as two local regimes:

- an early core Hf -> W,
- a late core Os -> Hg,
- compared against the full Hf -> Hg block.

The goal is to see whether a two-core reading gives a better explanation than a
single repaired core for this cleaner d-block.

It writes a timestamped JSON summary and a short text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import statistics
import time
from pathlib import Path


FULL_FAMILY = [
    {"symbol": "Hf", "period": 6, "mass_u": 178.49, "radius_pm": 159.0, "ionization_ev": 6.8251},
    {"symbol": "Ta", "period": 6, "mass_u": 180.94788, "radius_pm": 146.0, "ionization_ev": 7.5496},
    {"symbol": "W", "period": 6, "mass_u": 183.84, "radius_pm": 139.0, "ionization_ev": 7.8640},
    {"symbol": "Re", "period": 6, "mass_u": 186.207, "radius_pm": 137.0, "ionization_ev": 7.8335},
    {"symbol": "Os", "period": 6, "mass_u": 190.23, "radius_pm": 135.0, "ionization_ev": 8.4382},
    {"symbol": "Ir", "period": 6, "mass_u": 192.217, "radius_pm": 136.0, "ionization_ev": 8.9670},
    {"symbol": "Pt", "period": 6, "mass_u": 195.084, "radius_pm": 139.0, "ionization_ev": 8.9588},
    {"symbol": "Au", "period": 6, "mass_u": 196.96657, "radius_pm": 144.0, "ionization_ev": 9.2255},
    {"symbol": "Hg", "period": 6, "mass_u": 200.592, "radius_pm": 151.0, "ionization_ev": 10.4375},
]

EARLY_CORE = [FULL_FAMILY[0], FULL_FAMILY[1], FULL_FAMILY[2]]
LATE_CORE = [FULL_FAMILY[4], FULL_FAMILY[5], FULL_FAMILY[6], FULL_FAMILY[7], FULL_FAMILY[8]]
R_H_EV = 13.6


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def trend(values: list[float]) -> str:
    if all(b > a for a, b in zip(values[:-1], values[1:])):
        return "increasing"
    if all(b < a for a, b in zip(values[:-1], values[1:])):
        return "decreasing"
    return "mixed"


def linear_fit_rmse(values: list[float]) -> float:
    x_values = list(range(len(values)))
    mean_x = statistics.fmean(x_values)
    mean_y = statistics.fmean(values)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, values))
    denominator = sum((x - mean_x) ** 2 for x in x_values)
    slope = numerator / denominator if denominator else 0.0
    intercept = mean_y - slope * mean_x
    residuals = [(y - (slope * x + intercept)) ** 2 for x, y in zip(x_values, values)]
    return math.sqrt(sum(residuals) / len(values))


def step_cv(values: list[float]) -> float:
    steps = [b - a for a, b in zip(values[:-1], values[1:])]
    mean_step = statistics.fmean(steps)
    if mean_step == 0:
        return float("inf")
    return statistics.pstdev(steps) / abs(mean_step)


def analyze_series(series: list[dict]) -> dict:
    evaluated = []
    radii = []
    ionization = []
    zeff = []
    masses = []

    for item in series:
        proxy = estimate_zeff(item["ionization_ev"], item["period"])
        evaluated.append({**item, "zeff_proxy": round(proxy, 6)})
        radii.append(item["radius_pm"])
        ionization.append(item["ionization_ev"])
        zeff.append(proxy)
        masses.append(item["mass_u"])

    return {
        "series": evaluated,
        "radius_trend": trend(radii),
        "ionization_trend": trend(ionization),
        "zeff_trend": trend(zeff),
        "mass_trend": trend(masses),
        "radius_rmse": linear_fit_rmse(radii),
        "ionization_rmse": linear_fit_rmse(ionization),
        "zeff_rmse": linear_fit_rmse(zeff),
        "mass_rmse": linear_fit_rmse(masses),
        "radius_step_cv": step_cv(radii),
        "ionization_step_cv": step_cv(ionization),
        "zeff_step_cv": step_cv(zeff),
        "mass_step_cv": step_cv(masses),
    }


def classify(full_metrics: dict, early_metrics: dict, late_metrics: dict) -> dict:
    full_broken = full_metrics["radius_trend"] == "mixed" or full_metrics["ionization_trend"] == "mixed"
    early_regular = early_metrics["radius_trend"] == "decreasing" and early_metrics["ionization_trend"] == "increasing"
    late_regular = late_metrics["radius_trend"] == "increasing" and late_metrics["ionization_trend"] == "mixed"
    any_core_more_regular = (
        early_metrics["zeff_rmse"] < full_metrics["zeff_rmse"]
        or late_metrics["zeff_rmse"] < full_metrics["zeff_rmse"]
    )

    if full_broken and any_core_more_regular:
        verdict = "supported"
    elif early_regular or late_regular:
        verdict = "partiel"
    else:
        verdict = "falsifie"

    return {
        "hypothesis": "the 5d block is best read as two local regimes plus anomalies, not one repaired core",
        "case_control": "full 5d block Hf -> Hg versus early core Hf -> W and late core Os -> Hg",
        "observable": "whether splitting the block into two cores improves the regularity signal",
        "expected": {
            "full_family": "mixed or broken trend",
            "early_core": "distinct core behavior",
            "late_core": "distinct core behavior",
        },
        "measured": {
            "full_family": full_metrics,
            "early_core": early_metrics,
            "late_core": late_metrics,
        },
        "verdict": verdict,
        "reference": "5d block anomalies around Re, Ir, Pt and Hg",
        "falsifiers": [
            "the full 5d block is already regular",
            "the split into two cores does not change the regularity picture",
            "neither core is more regular than the full block",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    full_metrics = analyze_series(FULL_FAMILY)
    early_metrics = analyze_series(EARLY_CORE)
    late_metrics = analyze_series(LATE_CORE)
    results = classify(full_metrics, early_metrics, late_metrics)

    json_path = outdir / f"transition_5d_dual_core_view_check_{timestamp}.json"
    txt_path = outdir / f"transition_5d_dual_core_view_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Vue a deux noyaux sur le bloc de transition 5d\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Bloc complet:\n")
        handle.write(f"- radius_trend: {full_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {full_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {full_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {full_metrics['mass_trend']}\n\n")
        handle.write("Noyau precoce Hf -> W:\n")
        handle.write(f"- radius_trend: {early_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {early_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {early_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {early_metrics['mass_trend']}\n\n")
        handle.write("Noyau tardif Os -> Hg:\n")
        handle.write(f"- radius_trend: {late_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {late_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {late_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {late_metrics['mass_trend']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")
        handle.write(f"\nReference: {results['reference']}\n")
        handle.write(f"JSON: {json_path}\n")
        handle.write(f"TXT: {txt_path}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['verdict']}")


if __name__ == "__main__":
    main()