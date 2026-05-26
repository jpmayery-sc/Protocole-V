"""Compare fine tetrel subseries to see where mass becomes useful again.

The test splits the tetrel family at Ge:
- light core: C -> Si -> Ge
- heavy tail: Ge -> Sn -> Pb

The hypothesis is that Z_eff remains the better organizer in the light core,
while mass becomes competitive or better in the heavy tail.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6
FAMILY = [
    {"symbol": "C", "name": "Carbon", "period": 2, "mass_u": 12.011, "radius_pm": 67.0, "ionization_ev": 11.2603},
    {"symbol": "Si", "name": "Silicon", "period": 3, "mass_u": 28.085, "radius_pm": 111.0, "ionization_ev": 8.1517},
    {"symbol": "Ge", "name": "Germanium", "period": 4, "mass_u": 72.630, "radius_pm": 125.0, "ionization_ev": 7.8994},
    {"symbol": "Sn", "name": "Tin", "period": 5, "mass_u": 118.710, "radius_pm": 145.0, "ionization_ev": 7.3439},
    {"symbol": "Pb", "name": "Lead", "period": 6, "mass_u": 207.200, "radius_pm": 154.0, "ionization_ev": 7.4167},
]

LIGHT_CORE = FAMILY[:3]
HEAVY_TAIL = FAMILY[2:]


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


def analyze_series(series: list[dict]) -> dict:
    evaluated = []
    radii = []
    masses = []
    ionization_energies = []
    zeff_values = []

    for item in series:
        principal_n = item["period"]
        zeff = estimate_zeff(item["ionization_ev"], principal_n)
        evaluated.append({**item, "principal_n": principal_n, "zeff_proxy": round(zeff, 6)})
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


def classify(light_metrics: dict, heavy_metrics: dict) -> dict:
    light_zeff_better = light_metrics["zeff_rmse"] < light_metrics["mass_rmse"] and light_metrics["zeff_step_cv"] < light_metrics["mass_step_cv"]
    heavy_mass_better = heavy_metrics["mass_rmse"] <= heavy_metrics["zeff_rmse"] and heavy_metrics["mass_step_cv"] <= heavy_metrics["zeff_step_cv"]
    structural_ok = (
        light_metrics["radius_trend"] == "increasing"
        and light_metrics["ionization_trend"] == "decreasing"
        and heavy_metrics["radius_trend"] == "increasing"
        and heavy_metrics["ionization_trend"] == "decreasing"
    )

    if structural_ok and light_zeff_better and heavy_mass_better:
        verdict = "supported"
    elif structural_ok and (light_zeff_better or heavy_mass_better):
        verdict = "partiel"
    else:
        verdict = "falsifie"

    return {
        "hypothesis": "when the tetrel family is split at Ge, Z_eff stays better in the light core while mass regains usefulness in the heavy tail",
        "case_control": "C -> Si -> Ge versus Ge -> Sn -> Pb",
        "observable": "relative regularity of radius, ionization, Z_eff proxy and mass in the two subseries",
        "expected": {
            "light_core": "Z_eff smoother than mass",
            "heavy_tail": "mass competitive with or smoother than Z_eff",
        },
        "measured": {
            "light_core": light_metrics,
            "heavy_tail": heavy_metrics,
        },
        "criteria": {
            "light_zeff_better": light_zeff_better,
            "heavy_mass_better": heavy_mass_better,
            "structural_ok": structural_ok,
        },
        "verdict": verdict,
        "falsifiers": [
            "the light core is not monotone in radius and ionization",
            "Z_eff is not smoother than mass in the light core",
            "mass is not as good as or better than Z_eff in the heavy tail",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare fine tetrel subseries and test whether mass returns as a useful organizer.")
    _ = parser.parse_args()

    root = Path(__file__).resolve().parents[1]
    outdir = root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    light_metrics = analyze_series(LIGHT_CORE)
    heavy_metrics = analyze_series(HEAVY_TAIL)
    results = classify(light_metrics, heavy_metrics)

    json_path = outdir / f"tetrel_subseries_mass_return_check_{timestamp}.json"
    txt_path = outdir / f"tetrel_subseries_mass_return_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Tetrel subseries mass-return check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {results['hypothesis']}\n")
        handle.write(f"Cas de controle: {results['case_control']}\n")
        handle.write(f"Observable: {results['observable']}\n")
        handle.write(f"Verdict: {results['verdict']}\n\n")
        handle.write("Sous-serie legere C -> Ge:\n")
        for key, value in light_metrics.items():
            if key == "series":
                continue
            handle.write(f"- {key}: {value}\n")
        handle.write("\nSous-serie lourde Ge -> Pb:\n")
        for key, value in heavy_metrics.items():
            if key == "series":
                continue
            handle.write(f"- {key}: {value}\n")
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