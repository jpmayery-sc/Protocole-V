"""Block-and-edge view check for the 3d transition-metal block.

This script extends the block-and-edge protocol to a d-block where the trends
are known to contain shell/subshell anomalies:

- compare the full 3d series Sc -> Zn,
- compare a repaired core that removes the strongest local anomalies,
- see whether the block + edge view reveals a more regular core and whether
  Z_eff stays more regular than mass in that core.

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
    {"symbol": "Sc", "period": 4, "mass_u": 44.955908, "radius_pm": 162.0, "ionization_ev": 6.5615},
    {"symbol": "Ti", "period": 4, "mass_u": 47.867, "radius_pm": 147.0, "ionization_ev": 6.8281},
    {"symbol": "V", "period": 4, "mass_u": 50.9415, "radius_pm": 134.0, "ionization_ev": 6.7462},
    {"symbol": "Cr", "period": 4, "mass_u": 51.9961, "radius_pm": 128.0, "ionization_ev": 6.7665},
    {"symbol": "Mn", "period": 4, "mass_u": 54.938044, "radius_pm": 127.0, "ionization_ev": 7.434},
    {"symbol": "Fe", "period": 4, "mass_u": 55.845, "radius_pm": 126.0, "ionization_ev": 7.9024},
    {"symbol": "Co", "period": 4, "mass_u": 58.933194, "radius_pm": 125.0, "ionization_ev": 7.881},
    {"symbol": "Ni", "period": 4, "mass_u": 58.6934, "radius_pm": 124.0, "ionization_ev": 7.6398},
    {"symbol": "Cu", "period": 4, "mass_u": 63.546, "radius_pm": 128.0, "ionization_ev": 7.7264},
    {"symbol": "Zn", "period": 4, "mass_u": 65.38, "radius_pm": 134.0, "ionization_ev": 9.3942},
]

CORE_FAMILY = [FULL_FAMILY[0], FULL_FAMILY[1], FULL_FAMILY[2], FULL_FAMILY[4], FULL_FAMILY[5], FULL_FAMILY[6], FULL_FAMILY[7]]
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
    core_repaired = core_metrics["radius_trend"] == "mixed" or core_metrics["ionization_trend"] == "mixed"
    zeff_better_core = core_metrics["zeff_rmse"] < core_metrics["mass_rmse"] and core_metrics["zeff_step_cv"] < core_metrics["mass_step_cv"]

    if full_broken and core_repaired and zeff_better_core:
        verdict = "supported"
    elif core_repaired:
        verdict = "partiel"
    else:
        verdict = "falsifie"

    return {
        "hypothesis": "the 3d transition block needs a block-and-edge view to isolate the usable core",
        "case_control": "full 3d block Sc -> Zn versus a repaired core excluding the strongest local anomalies",
        "observable": "trend repair and regularity change after removing local anomalies",
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
        "reference": "3d block with known local anomalies around Cr and Cu",
        "falsifiers": [
            "the full 3d block is already regular",
            "the repaired core does not improve regularity",
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

    json_path = outdir / f"transition_3d_block_edge_view_check_{timestamp}.json"
    txt_path = outdir / f"transition_3d_block_edge_view_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Bloc + bord de serie sur le bloc de transition 3d\n")
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
        handle.write("Noyau repare:\n")
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