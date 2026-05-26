"""Check whether the heavy tetrel endpoint leaves a residual after Z_eff correction.

The script compares the full tetrel family C -> Pb against the refined core
C -> Sn. The hypothesis is that Pb still carries a local residual after a
simple radius-vs-Z_eff correction, even when the subfamily remains smoother.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


FULL_FAMILY = [
    {"symbol": "C", "name": "Carbon", "period": 2, "mass_u": 12.011, "radius_pm": 67.0, "ionization_ev": 11.2603},
    {"symbol": "Si", "name": "Silicon", "period": 3, "mass_u": 28.085, "radius_pm": 111.0, "ionization_ev": 8.1517},
    {"symbol": "Ge", "name": "Germanium", "period": 4, "mass_u": 72.630, "radius_pm": 125.0, "ionization_ev": 7.8994},
    {"symbol": "Sn", "name": "Tin", "period": 5, "mass_u": 118.710, "radius_pm": 145.0, "ionization_ev": 7.3439},
    {"symbol": "Pb", "name": "Lead", "period": 6, "mass_u": 207.2, "radius_pm": 154.0, "ionization_ev": 7.4167},
]

CORE_FAMILY = FULL_FAMILY[:-1]
R_H_EV = 13.6


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = numerator / denominator if denominator else 0.0
    intercept = mean_y - slope * mean_x
    return slope, intercept


def residual_metrics(series: list[dict]) -> dict:
    evaluated = []
    zeff_values = []
    radii = []
    masses = []
    periods = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        evaluated.append({**item, "zeff_proxy": round(zeff, 6)})
        zeff_values.append(zeff)
        radii.append(item["radius_pm"])
        masses.append(item["mass_u"])
        periods.append(item["period"])

    zeff_slope, zeff_intercept = linear_fit(zeff_values, radii)
    mass_slope, mass_intercept = linear_fit(masses, radii)

    for item, zeff_value, mass_value, radius in zip(evaluated, zeff_values, masses, radii):
        zeff_pred = zeff_slope * zeff_value + zeff_intercept
        mass_pred = mass_slope * mass_value + mass_intercept
        item["zeff_residual"] = radius - zeff_pred
        item["mass_residual"] = radius - mass_pred

    zeff_residuals = [item["zeff_residual"] for item in evaluated]
    mass_residuals = [item["mass_residual"] for item in evaluated]

    abs_zeff_residuals = [abs(value) for value in zeff_residuals]
    abs_mass_residuals = [abs(value) for value in mass_residuals]

    endpoint_symbol = evaluated[-1]["symbol"]

    return {
        "series": evaluated,
        "zeff_fit": {"slope": zeff_slope, "intercept": zeff_intercept},
        "mass_fit": {"slope": mass_slope, "intercept": mass_intercept},
        "zeff_max_abs_residual": max(abs_zeff_residuals),
        "mass_max_abs_residual": max(abs_mass_residuals),
        "zeff_mean_abs_residual": statistics.fmean(abs_zeff_residuals),
        "mass_mean_abs_residual": statistics.fmean(abs_mass_residuals),
        "endpoint_symbol": endpoint_symbol,
        "endpoint_zeff_residual": evaluated[-1]["zeff_residual"],
        "endpoint_mass_residual": evaluated[-1]["mass_residual"],
        "radius_trend": "increasing" if all(b > a for a, b in zip(radii[:-1], radii[1:])) else "mixed",
        "zeff_trend": "increasing" if all(b > a for a, b in zip(zeff_values[:-1], zeff_values[1:])) else "mixed",
        "mass_trend": "increasing" if all(b > a for a, b in zip(masses[:-1], masses[1:])) else "mixed",
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    full_metrics = residual_metrics(FULL_FAMILY)
    core_metrics = residual_metrics(CORE_FAMILY)

    heavy_residual_ok = abs(full_metrics["endpoint_zeff_residual"]) > abs(core_metrics["endpoint_zeff_residual"])
    core_cleaner_ok = core_metrics["zeff_mean_abs_residual"] < full_metrics["zeff_mean_abs_residual"]
    zeff_better_than_mass = full_metrics["zeff_mean_abs_residual"] < full_metrics["mass_mean_abs_residual"]
    verdict = "supported" if heavy_residual_ok and core_cleaner_ok and zeff_better_than_mass else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "heavy_residual_ok": heavy_residual_ok,
        "core_cleaner_ok": core_cleaner_ok,
        "zeff_better_than_mass": zeff_better_than_mass,
        "full_family": full_metrics,
        "core_family": core_metrics,
        "hypothesis": "the heavy tetrel endpoint Pb leaves a residual after Z_eff correction that is reduced in the refined core",
        "case_control": "full C -> Pb tetrel family versus core C -> Sn",
        "observable": "mean and endpoint residuals after fitting radius against Z_eff proxy",
    }

    json_path = outdir / f"tetrel_zeff_residual_check_{timestamp}.json"
    txt_path = outdir / f"tetrel_zeff_residual_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Tetrel Z_eff residual check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {data['hypothesis']}\n")
        handle.write(f"Cas de controle: {data['case_control']}\n")
        handle.write(f"Observable: {data['observable']}\n")
        handle.write(f"Verdict: {verdict}\n\n")
        handle.write("Bloc complet C -> Pb:\n")
        handle.write(f"- radius_trend: {full_metrics['radius_trend']}\n")
        handle.write(f"- zeff_trend: {full_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {full_metrics['mass_trend']}\n")
        handle.write(f"- zeff_mean_abs_residual: {full_metrics['zeff_mean_abs_residual']:.6f}\n")
        handle.write(f"- mass_mean_abs_residual: {full_metrics['mass_mean_abs_residual']:.6f}\n")
        handle.write(f"- endpoint_symbol: {full_metrics['endpoint_symbol']}\n")
        handle.write(f"- endpoint_zeff_residual: {full_metrics['endpoint_zeff_residual']:.6f}\n")
        handle.write(f"- endpoint_mass_residual: {full_metrics['endpoint_mass_residual']:.6f}\n\n")
        handle.write("Noyau repare C -> Sn:\n")
        handle.write(f"- zeff_mean_abs_residual: {core_metrics['zeff_mean_abs_residual']:.6f}\n")
        handle.write(f"- mass_mean_abs_residual: {core_metrics['mass_mean_abs_residual']:.6f}\n")
        handle.write(f"- zeff_max_abs_residual: {core_metrics['zeff_max_abs_residual']:.6f}\n")
        handle.write(f"- mass_max_abs_residual: {core_metrics['mass_max_abs_residual']:.6f}\n")
        handle.write("\nFalsificateurs:\n")
        handle.write("- Pb ne laisse pas de residu plus fort que la moyenne du bloc complet\n")
        handle.write("- le noyau C -> Sn n est pas plus propre que le bloc complet\n")
        handle.write("- Z_eff n ameliore pas la regularite par rapport a la masse\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {verdict}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    run_check(args.output_dir)


if __name__ == "__main__":
    main()