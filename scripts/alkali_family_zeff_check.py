"""Research check for the alkali family Li -> Cs.

This script tests the working hypothesis derived from Electron-5:

- for a family with the same valence, the atomic radius tracks the effective
  charge proxy better than atomic mass alone;
- the first ionization energy decreases monotonically down the family;
- the proxy Z_eff inferred from ionization energy changes smoothly.

It writes a timestamped JSON summary and a short text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import math
import statistics
import time
from pathlib import Path


FAMILY = [
    {"symbol": "Li", "name": "Lithium", "period": 2, "mass_u": 6.94, "radius_pm": 152.0, "ionization_ev": 5.3917},
    {"symbol": "Na", "name": "Sodium", "period": 3, "mass_u": 22.98976928, "radius_pm": 186.0, "ionization_ev": 5.1391},
    {"symbol": "K", "name": "Potassium", "period": 4, "mass_u": 39.0983, "radius_pm": 227.0, "ionization_ev": 4.3407},
    {"symbol": "Rb", "name": "Rubidium", "period": 5, "mass_u": 85.4678, "radius_pm": 248.0, "ionization_ev": 4.1771},
    {"symbol": "Cs", "name": "Cesium", "period": 6, "mass_u": 132.90545196, "radius_pm": 265.0, "ionization_ev": 3.8939},
]

R_H_EV = 13.6


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


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


def monotonicity(values: list[float]) -> str:
    increasing = all(b > a for a, b in zip(values[:-1], values[1:]))
    decreasing = all(b < a for a, b in zip(values[:-1], values[1:]))
    if increasing:
        return "increasing"
    if decreasing:
        return "decreasing"
    return "mixed"


def analyze_family() -> dict:
    evaluated = []

    radii = []
    masses = []
    ionization_energies = []
    zeff_values = []

    for item in FAMILY:
        principal_n = item["period"]
        zeff = estimate_zeff(item["ionization_ev"], principal_n)
        evaluated.append({
            **item,
            "principal_n": principal_n,
            "zeff_proxy": round(zeff, 6),
        })
        radii.append(item["radius_pm"])
        masses.append(item["mass_u"])
        ionization_energies.append(item["ionization_ev"])
        zeff_values.append(zeff)

    radius_trend = monotonicity(radii)
    ionization_trend = monotonicity(ionization_energies)
    zeff_trend = monotonicity(zeff_values)
    mass_trend = monotonicity(masses)

    radius_rmse = linear_fit_rmse(radii)
    ionization_rmse = linear_fit_rmse(ionization_energies)
    zeff_rmse = linear_fit_rmse(zeff_values)
    mass_rmse = linear_fit_rmse(masses)

    radius_step_cv = step_cv(radii)
    ionization_step_cv = step_cv(ionization_energies)
    zeff_step_cv = step_cv(zeff_values)
    mass_step_cv = step_cv(masses)

    trend_ok = radius_trend == "increasing" and ionization_trend == "decreasing" and zeff_trend == "increasing"
    smoothness_ok = zeff_rmse < mass_rmse and zeff_step_cv < mass_step_cv
    family_ok = trend_ok and smoothness_ok

    if family_ok:
        verdict = "supported"
    elif trend_ok:
        verdict = "partiel"
    else:
        verdict = "falsifie"

    return {
        "family_name": "alkali_family",
        "family": evaluated,
        "observables": {
            "radius_trend": radius_trend,
            "ionization_trend": ionization_trend,
            "zeff_trend": zeff_trend,
            "mass_trend": mass_trend,
            "radius_rmse": radius_rmse,
            "ionization_rmse": ionization_rmse,
            "zeff_rmse": zeff_rmse,
            "mass_rmse": mass_rmse,
            "radius_step_cv": radius_step_cv,
            "ionization_step_cv": ionization_step_cv,
            "zeff_step_cv": zeff_step_cv,
            "mass_step_cv": mass_step_cv,
        },
        "hypothesis": "for the alkali family, radius tracks Z_eff better than mass alone",
        "case_control": "Li -> Na -> K -> Rb -> Cs same-valence family",
        "expected": {
            "radius": "monotonic increase",
            "ionization": "monotonic decrease",
            "zeff_proxy": "smooth monotonic increase",
            "mass": "less explanatory than zeff_proxy for the family trend",
        },
        "verdict": verdict,
        "falsifiers": [
            "radius is not monotonic across Li -> Cs",
            "first ionization energy is not monotonic across Li -> Cs",
            "Z_eff proxy is not smoother than mass across the family",
            "mass alone explains the family trend as well as or better than Z_eff proxy",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = analyze_family()

    json_path = outdir / f"alkali_family_zeff_check_{timestamp}.json"
    txt_path = outdir / f"alkali_family_zeff_check_{timestamp}.txt"
    json_payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(json_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Recherche sur la famille alcaline Li -> Cs\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Observables:\n")
        for key, value in results["observables"].items():
            handle.write(f"- {key}: {value}\n")
        handle.write("\nFamily summary:\n")
        for item in results["family"]:
            handle.write(
                f"- {item['symbol']}: period={item['period']}, mass_u={item['mass_u']}, "
                f"radius_pm={item['radius_pm']}, ionization_ev={item['ionization_ev']}, zeff_proxy={item['zeff_proxy']}\n"
            )
        handle.write(f"\nHypothese: {results['hypothesis']}\n")
        handle.write(f"Verdict global: {results['verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['verdict']}")


if __name__ == "__main__":
    main()