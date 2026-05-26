"""Finer residual check for the lanthanide f-block.

This script tests whether the two internal anomalies Eu and Yb explain most of
the irregularity of the lanthanide family. It compares:
- the full family La -> Lu,
- a repaired core excluding Eu and Yb.

The repaired core is expected to be smoother than the full family, and Z_eff
should remain more regular than mass in that repaired core.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6

FULL_FAMILY = [
    {"symbol": "La", "period": 6, "mass_u": 138.90547, "radius_pm": 195.0, "ionization_ev": 5.5770},
    {"symbol": "Ce", "period": 6, "mass_u": 140.11600, "radius_pm": 185.0, "ionization_ev": 5.5387},
    {"symbol": "Pr", "period": 6, "mass_u": 140.90766, "radius_pm": 182.0, "ionization_ev": 5.4730},
    {"symbol": "Nd", "period": 6, "mass_u": 144.24200, "radius_pm": 181.0, "ionization_ev": 5.5250},
    {"symbol": "Sm", "period": 6, "mass_u": 150.36000, "radius_pm": 180.0, "ionization_ev": 5.6440},
    {"symbol": "Eu", "period": 6, "mass_u": 151.96400, "radius_pm": 199.0, "ionization_ev": 5.6700},
    {"symbol": "Gd", "period": 6, "mass_u": 157.25000, "radius_pm": 180.0, "ionization_ev": 6.1500},
    {"symbol": "Tb", "period": 6, "mass_u": 158.92535, "radius_pm": 178.0, "ionization_ev": 5.8630},
    {"symbol": "Dy", "period": 6, "mass_u": 162.50000, "radius_pm": 177.0, "ionization_ev": 5.9390},
    {"symbol": "Ho", "period": 6, "mass_u": 164.93033, "radius_pm": 176.0, "ionization_ev": 6.0220},
    {"symbol": "Er", "period": 6, "mass_u": 167.25900, "radius_pm": 175.0, "ionization_ev": 6.1080},
    {"symbol": "Tm", "period": 6, "mass_u": 168.93422, "radius_pm": 174.0, "ionization_ev": 6.1840},
    {"symbol": "Yb", "period": 6, "mass_u": 173.04500, "radius_pm": 194.0, "ionization_ev": 6.2540},
    {"symbol": "Lu", "period": 6, "mass_u": 174.96680, "radius_pm": 173.0, "ionization_ev": 5.4280},
]

REPAIRED_CORE = [item for item in FULL_FAMILY if item["symbol"] not in {"Eu", "Yb"}]


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
    if not steps:
        return float("nan")
    mean_step = statistics.fmean(steps)
    if mean_step == 0.0:
        return float("inf")
    return statistics.pstdev(steps) / abs(mean_step)


def analyze_family(series: list[dict]) -> dict:
    evaluated = []
    radii = []
    masses = []
    ionization_energies = []
    zeff_values = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        evaluated.append({**item, "zeff_proxy": round(zeff, 6)})
        radii.append(item["radius_pm"])
        masses.append(item["mass_u"])
        ionization_energies.append(item["ionization_ev"])
        zeff_values.append(zeff)

    return {
        "series": evaluated,
        "radius_trend": trend(radii),
        "ionization_trend": trend(ionization_energies),
        "zeff_trend": trend(zeff_values),
        "mass_trend": trend(masses),
        "radius_rmse": linear_fit_rmse(radii),
        "ionization_rmse": linear_fit_rmse(ionization_energies),
        "zeff_rmse": linear_fit_rmse(zeff_values),
        "mass_rmse": linear_fit_rmse(masses),
        "radius_step_cv": step_cv(radii),
        "ionization_step_cv": step_cv(ionization_energies),
        "zeff_step_cv": step_cv(zeff_values),
        "mass_step_cv": step_cv(masses),
    }


def classify(full_metrics: dict, repaired_metrics: dict) -> dict:
    full_broken = full_metrics["radius_trend"] == "mixed" or full_metrics["ionization_trend"] == "mixed"
    repaired_cleaner = repaired_metrics["radius_rmse"] < full_metrics["radius_rmse"] and repaired_metrics["radius_step_cv"] < full_metrics["radius_step_cv"]
    zeff_better = repaired_metrics["zeff_rmse"] < repaired_metrics["mass_rmse"]
    structural_ok = repaired_metrics["radius_trend"] == "mixed" or repaired_metrics["radius_trend"] == "decreasing" or repaired_metrics["radius_trend"] == "increasing"

    if full_broken and repaired_cleaner and zeff_better:
        verdict = "supported"
    elif repaired_cleaner or zeff_better:
        verdict = "partiel"
    else:
        verdict = "falsifie"

    return {
        "hypothesis": "removing Eu and Yb repairs most of the internal f-block residual, and Z_eff remains more regular than mass in the repaired core",
        "case_control": "full lanthanide family La -> Lu versus repaired core excluding Eu and Yb",
        "observable": "trend repair and regularity change after removing the two internal anomalies",
        "expected": {
            "full_family": "mixed or broken trend",
            "repaired_core": "more regular than the full series",
            "z_eff": "more regular than mass in the repaired core by fit quality",
            "ionization": "may remain mixed even after the repair",
        },
        "measured": {
            "full_family": full_metrics,
            "repaired_core": repaired_metrics,
        },
        "criteria": {
            "full_broken": full_broken,
            "repaired_cleaner": repaired_cleaner,
            "zeff_better": zeff_better,
            "structural_ok": structural_ok,
        },
        "verdict": verdict,
        "falsifiers": [
            "the full family is already regular",
            "removing Eu and Yb does not improve radius regularity",
            "Z_eff is not more regular than mass in the repaired core",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Finer lanthanide residual check excluding Eu and Yb.")
    _ = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    outdir = root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    full_metrics = analyze_family(FULL_FAMILY)
    repaired_metrics = analyze_family(REPAIRED_CORE)
    results = classify(full_metrics, repaired_metrics)

    json_path = outdir / f"lanthanide_internal_residual_check_{timestamp}.json"
    txt_path = outdir / f"lanthanide_internal_residual_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Lanthanide internal residual check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Famille complete:\n")
        for key in ["radius_trend", "ionization_trend", "zeff_trend", "mass_trend", "radius_rmse", "ionization_rmse", "zeff_rmse", "mass_rmse"]:
            handle.write(f"- {key}: {full_metrics[key]}\n")
        handle.write("\nNoyau repare (sans Eu et Yb):\n")
        for key in ["radius_trend", "ionization_trend", "zeff_trend", "mass_trend", "radius_rmse", "ionization_rmse", "zeff_rmse", "mass_rmse"]:
            handle.write(f"- {key}: {repaired_metrics[key]}\n")
        handle.write("\nCriteres:\n")
        for key, value in results["criteria"].items():
            handle.write(f"- {key}: {value}\n")
        handle.write("\nFalsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['verdict']}")


if __name__ == "__main__":
    main()