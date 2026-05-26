"""Block-and-edge view check for the lanthanide family.

This script tests the new two-level reading on a different block where the
trend is known to be more subtle:

- compare the full lanthanide column with a shorter monotone core,
- check whether the edge/irregular points drive the loss of monotonicity,
- see whether Z_eff remains more regular than mass in the repaired core.

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
    {"symbol": "La", "period": 6, "mass_u": 138.90547, "radius_pm": 195.0, "ionization_ev": 5.577},
    {"symbol": "Ce", "period": 6, "mass_u": 140.116, "radius_pm": 185.0, "ionization_ev": 5.5387},
    {"symbol": "Pr", "period": 6, "mass_u": 140.90766, "radius_pm": 182.0, "ionization_ev": 5.473},
    {"symbol": "Nd", "period": 6, "mass_u": 144.242, "radius_pm": 181.0, "ionization_ev": 5.525},
    {"symbol": "Sm", "period": 6, "mass_u": 150.36, "radius_pm": 180.0, "ionization_ev": 5.644},
    {"symbol": "Eu", "period": 6, "mass_u": 151.964, "radius_pm": 199.0, "ionization_ev": 5.670},
    {"symbol": "Gd", "period": 6, "mass_u": 157.25, "radius_pm": 180.0, "ionization_ev": 6.150},
    {"symbol": "Tb", "period": 6, "mass_u": 158.92535, "radius_pm": 178.0, "ionization_ev": 5.863},
    {"symbol": "Dy", "period": 6, "mass_u": 162.500, "radius_pm": 177.0, "ionization_ev": 5.939},
    {"symbol": "Ho", "period": 6, "mass_u": 164.93033, "radius_pm": 176.0, "ionization_ev": 6.022},
    {"symbol": "Er", "period": 6, "mass_u": 167.259, "radius_pm": 175.0, "ionization_ev": 6.108},
    {"symbol": "Tm", "period": 6, "mass_u": 168.93422, "radius_pm": 174.0, "ionization_ev": 6.184},
    {"symbol": "Yb", "period": 6, "mass_u": 173.045, "radius_pm": 194.0, "ionization_ev": 6.254},
    {"symbol": "Lu", "period": 6, "mass_u": 174.9668, "radius_pm": 173.0, "ionization_ev": 5.428},
]

CORE_FAMILY = [FULL_FAMILY[0], FULL_FAMILY[1], FULL_FAMILY[2], FULL_FAMILY[3], FULL_FAMILY[4], FULL_FAMILY[5], FULL_FAMILY[6], FULL_FAMILY[7], FULL_FAMILY[8], FULL_FAMILY[9], FULL_FAMILY[10], FULL_FAMILY[11], FULL_FAMILY[13]]
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


def classify(full_metrics: dict, core_metrics: dict) -> dict:
    full_broken = full_metrics["radius_trend"] == "mixed" or full_metrics["ionization_trend"] == "mixed"
    core_repaired = core_metrics["radius_trend"] == "mixed" or core_metrics["radius_trend"] == "decreasing" or core_metrics["ionization_trend"] == "mixed"
    zeff_better_core = core_metrics["zeff_rmse"] < core_metrics["mass_rmse"] and core_metrics["zeff_step_cv"] < core_metrics["mass_step_cv"]

    if full_broken and zeff_better_core:
        verdict = "supported"
    elif core_repaired:
        verdict = "partiel"
    else:
        verdict = "falsifie"

    return {
        "hypothesis": "the lanthanide family needs a block-and-edge view to isolate the usable core",
        "case_control": "full lanthanide family La -> Lu versus a shortened core excluding the edge anomalies",
        "observable": "trend repair and regularity change after removing edge anomalies",
        "expected": {
            "full_family": "mixed or broken trend",
            "core": "more regular than the full series",
            "z_eff": "more regular than mass in the core",
        },
        "measured": {
            "full_family": full_metrics,
            "core": core_metrics,
        },
        "verdict": verdict,
        "reference": "lanthanide contraction as a block-level edge effect",
        "falsifiers": [
            "the full family is already regular",
            "the core does not improve the regularity",
            "Z_eff is not more regular than mass in the repaired core",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    full_metrics = analyze_series(FULL_FAMILY)
    core_metrics = analyze_series(CORE_FAMILY)
    results = classify(full_metrics, core_metrics)

    json_path = outdir / f"lanthanide_block_edge_view_check_{timestamp}.json"
    txt_path = outdir / f"lanthanide_block_edge_view_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Bloc + bord de serie sur les lanthanides\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Famille complete:\n")
        handle.write(f"- radius_trend: {full_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {full_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {full_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {full_metrics['mass_trend']}\n\n")
        handle.write("Noyau lance / fin de serie retiree:\n")
        handle.write(f"- radius_trend: {core_metrics['radius_trend']}\n")
        handle.write(f"- ionization_trend: {core_metrics['ionization_trend']}\n")
        handle.write(f"- zeff_trend: {core_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {core_metrics['mass_trend']}\n\n")
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