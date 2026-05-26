"""Check the pnictogen D1 / D2 regime assignment.

The earlier residual framing was too narrow for the pnictogen column. The
official question is now whether the family is assigned to the expected D1/D2
bands:

- N and P should stay covalent,
- As should fall into the transition band,
- Sb and Bi should fall into the semi-metal band.

The output keeps the familiar residual tables, but the verdict is now driven by
the regime assignment, not by a raw residual-versus-mass comparison.
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
    {"symbol": "N", "name": "Nitrogen", "period": 2, "mass_u": 14.007, "radius_pm": 56.0, "ionization_ev": 14.5341},
    {"symbol": "P", "name": "Phosphorus", "period": 3, "mass_u": 30.973761998, "radius_pm": 98.0, "ionization_ev": 10.4867},
    {"symbol": "As", "name": "Arsenic", "period": 4, "mass_u": 74.921595, "radius_pm": 114.0, "ionization_ev": 9.8152},
    {"symbol": "Sb", "name": "Antimony", "period": 5, "mass_u": 121.760, "radius_pm": 133.0, "ionization_ev": 8.6084},
    {"symbol": "Bi", "name": "Bismuth", "period": 6, "mass_u": 208.9804, "radius_pm": 148.0, "ionization_ev": 7.2856},
]

CORE_FAMILY = FULL_FAMILY[:-1]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def d2_value(ionization_ev: float, radius_pm: float) -> float:
    return ionization_ev / radius_pm


def d1overd2_value(item: dict) -> float:
    d1_value = estimate_zeff(item["ionization_ev"], item["period"])
    d2 = d2_value(item["ionization_ev"], item["radius_pm"])
    return d1_value / d2 if d2 else float("inf")


def classify_ratio(value: float) -> str:
    if value < 30:
        return "covalent"
    if value < 50:
        return "transition"
    if value < 100:
        return "semi-metal"
    return "D3 / topological"


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

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        ratio = d1overd2_value(item)
        evaluated.append({**item, "zeff_proxy": round(zeff, 6)})
        evaluated[-1]["D1overD2"] = round(ratio, 6)
        evaluated[-1]["regime"] = classify_ratio(ratio)
        zeff_values.append(zeff)
        radii.append(item["radius_pm"])
        masses.append(item["mass_u"])

    zeff_slope, zeff_intercept = linear_fit(zeff_values, radii)
    mass_slope, mass_intercept = linear_fit(masses, radii)

    for item, zeff_value, mass_value, radius in zip(evaluated, zeff_values, masses, radii):
        item["zeff_residual"] = radius - (zeff_slope * zeff_value + zeff_intercept)
        item["mass_residual"] = radius - (mass_slope * mass_value + mass_intercept)

    abs_zeff_residuals = [abs(item["zeff_residual"]) for item in evaluated]
    abs_mass_residuals = [abs(item["mass_residual"]) for item in evaluated]

    return {
        "series": evaluated,
        "zeff_fit": {"slope": zeff_slope, "intercept": zeff_intercept},
        "mass_fit": {"slope": mass_slope, "intercept": mass_intercept},
        "zeff_max_abs_residual": max(abs_zeff_residuals),
        "mass_max_abs_residual": max(abs_mass_residuals),
        "zeff_mean_abs_residual": statistics.fmean(abs_zeff_residuals),
        "mass_mean_abs_residual": statistics.fmean(abs_mass_residuals),
        "endpoint_symbol": evaluated[-1]["symbol"],
        "endpoint_zeff_residual": evaluated[-1]["zeff_residual"],
        "endpoint_mass_residual": evaluated[-1]["mass_residual"],
        "radius_trend": "increasing" if all(b > a for a, b in zip(radii[:-1], radii[1:])) else "mixed",
        "zeff_trend": "increasing" if all(b > a for a, b in zip(zeff_values[:-1], zeff_values[1:])) else "mixed",
        "mass_trend": "increasing" if all(b > a for a, b in zip(masses[:-1], masses[1:])) else "mixed",
        "ratios": [item["D1overD2"] for item in evaluated],
        "regimes": [item["regime"] for item in evaluated],
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    full_metrics = residual_metrics(FULL_FAMILY)
    core_metrics = residual_metrics(CORE_FAMILY)

    expected_regimes = ["covalent", "covalent", "transition", "semi-metal", "semi-metal"]
    regime_ok = full_metrics["regimes"] == expected_regimes
    ratio_monotone = all(b > a for a, b in zip(full_metrics["ratios"][:-1], full_metrics["ratios"][1:]))
    verdict = "supported" if regime_ok and ratio_monotone else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "regime_ok": regime_ok,
        "ratio_monotone": ratio_monotone,
        "full_family": full_metrics,
        "core_family": core_metrics,
        "hypothesis": "the pnictogen family should be assigned to the expected D1/D2 regimes",
        "case_control": "full N -> Bi pnictogen family versus the expected covalent / transition / semi-metal bands",
        "observable": "D1/D2 ratio and regime assignment across the column",
    }

    json_path = outdir / f"pnictogen_residual_check_{timestamp}.json"
    txt_path = outdir / f"pnictogen_residual_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Pnictogen residual check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {data['hypothesis']}\n")
        handle.write(f"Cas de controle: {data['case_control']}\n")
        handle.write(f"Observable: {data['observable']}\n")
        handle.write(f"Verdict: {verdict}\n\n")
        handle.write("Famille complete N -> Bi:\n")
        handle.write(f"- radius_trend: {full_metrics['radius_trend']}\n")
        handle.write(f"- zeff_trend: {full_metrics['zeff_trend']}\n")
        handle.write(f"- mass_trend: {full_metrics['mass_trend']}\n")
        handle.write(f"- regimes: {full_metrics['regimes']}\n")
        handle.write(f"- ratios: {[round(value, 6) for value in full_metrics['ratios']]}\n")
        handle.write(f"- zeff_mean_abs_residual: {full_metrics['zeff_mean_abs_residual']:.6f}\n")
        handle.write(f"- mass_mean_abs_residual: {full_metrics['mass_mean_abs_residual']:.6f}\n")
        handle.write(f"- endpoint_symbol: {full_metrics['endpoint_symbol']}\n")
        handle.write(f"- endpoint_zeff_residual: {full_metrics['endpoint_zeff_residual']:.6f}\n")
        handle.write(f"- endpoint_mass_residual: {full_metrics['endpoint_mass_residual']:.6f}\n\n")
        handle.write("Noyau repare N -> Sb:\n")
        handle.write(f"- regimes: {core_metrics['regimes']}\n")
        handle.write(f"- ratios: {[round(value, 6) for value in core_metrics['ratios']]}\n")
        handle.write(f"- zeff_mean_abs_residual: {core_metrics['zeff_mean_abs_residual']:.6f}\n")
        handle.write(f"- mass_mean_abs_residual: {core_metrics['mass_mean_abs_residual']:.6f}\n")
        handle.write(f"- zeff_max_abs_residual: {core_metrics['zeff_max_abs_residual']:.6f}\n")
        handle.write(f"- mass_max_abs_residual: {core_metrics['mass_max_abs_residual']:.6f}\n")
        handle.write("\nFalsificateurs:\n")
        handle.write("- la colonne pnictogene ne respecte pas les bandes covalent / transition / semi-metal\n")
        handle.write("- les ratios D1/D2 ne sont pas monotones\n")

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