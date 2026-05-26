"""Block-and-edge view check for the boron family B -> Tl.

This script applies the same two-level reading used for the tetrel family:

- compare the full family to a monotone subfamily,
- see whether the heavy edge is what breaks the trend,
- verify whether the block + edge view adds explanatory power.

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
    {"symbol": "B", "period": 2, "mass_u": 10.81, "radius_pm": 87.0, "ionization_ev": 8.298},
    {"symbol": "Al", "period": 3, "mass_u": 26.9815385, "radius_pm": 143.0, "ionization_ev": 5.9858},
    {"symbol": "Ga", "period": 4, "mass_u": 69.723, "radius_pm": 135.0, "ionization_ev": 5.9993},
    {"symbol": "In", "period": 5, "mass_u": 114.818, "radius_pm": 156.0, "ionization_ev": 5.7864},
    {"symbol": "Tl", "period": 6, "mass_u": 204.38, "radius_pm": 170.0, "ionization_ev": 6.1082},
]

SUB_FAMILY = [FULL_FAMILY[0], FULL_FAMILY[1], FULL_FAMILY[3]]
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


def classify(full_metrics: dict, sub_metrics: dict) -> dict:
    full_rerupture = full_metrics["radius_trend"] == "mixed" or full_metrics["ionization_trend"] == "mixed"
    sub_repair = sub_metrics["radius_trend"] == "increasing" and sub_metrics["ionization_trend"] == "decreasing"
    zeff_better_full = full_metrics["zeff_rmse"] < full_metrics["mass_rmse"] and full_metrics["zeff_step_cv"] < full_metrics["mass_step_cv"]
    zeff_better_sub = sub_metrics["zeff_rmse"] < sub_metrics["mass_rmse"] and sub_metrics["zeff_step_cv"] < sub_metrics["mass_step_cv"]

    if full_rerupture and sub_repair and zeff_better_sub:
        verdict = "supported"
    elif sub_repair:
        verdict = "partiel"
    else:
        verdict = "falsifie"

    return {
        "hypothesis": "the boron family needs a block-and-edge view to isolate the monotone core",
        "case_control": "full family B -> Tl versus subfamily B -> Al -> In",
        "observable": "trend repair and regularity change after removing the heavy edge and one internal rupture",
        "expected": {
            "full_family": "mixed or broken trend",
            "subfamily": "monotone trend",
            "zeff": "better regularity than mass in the subfamily",
        },
        "measured": {
            "full_family": full_metrics,
            "subfamily": sub_metrics,
        },
        "verdict": verdict,
        "reference": "boron family split at the irregular edge",
        "falsifiers": [
            "the full family is already monotone",
            "the subfamily does not repair the broken trend",
            "Z_eff is not more regular than mass in the repaired subfamily",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    full_metrics = analyze_series(FULL_FAMILY)
    sub_metrics = analyze_series(SUB_FAMILY)
    results = classify(full_metrics, sub_metrics)

    json_path = outdir / f"boron_block_edge_view_check_{timestamp}.json"
    txt_path = outdir / f"boron_block_edge_view_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Bloc + bord de serie sur la famille du bore\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Famille complete:\n")
        handle.write(f"- radius_trend: {full_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {full_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {full_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {full_metrics['mass_trend']}\n")
        handle.write(f"- zeff_rmse: {full_metrics['zeff_rmse']}\n")
        handle.write(f"- mass_rmse: {full_metrics['mass_rmse']}\n\n")
        handle.write("Sous-famille B -> Al -> In:\n")
        handle.write(f"- radius_trend: {sub_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {sub_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {sub_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {sub_metrics['mass_trend']}\n")
        handle.write(f"- zeff_rmse: {sub_metrics['zeff_rmse']}\n")
        handle.write(f"- mass_rmse: {sub_metrics['mass_rmse']}\n\n")
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