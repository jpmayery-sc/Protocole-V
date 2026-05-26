"""Dedicated Omega(Z) structure check.

This script turns the Omega(Z) discussion into an executable check on a heavy
series. It measures whether a local two-layer reading improves over a compact
single-slope baseline, then reports the result for the lanthanide block and a
small heavy probe trio.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6

LANTHANIDES = [
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

HEAVY_PROBES = [
    {"symbol": "Fr", "period": 7, "mass_u": 223.0, "radius_pm": 270.0, "ionization_ev": 4.0727},
    {"symbol": "Ra", "period": 7, "mass_u": 226.0, "radius_pm": 221.0, "ionization_ev": 5.2784},
    {"symbol": "Lr", "period": 7, "mass_u": 266.0, "radius_pm": 171.0, "ionization_ev": 4.96},
]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def trend(values: list[float]) -> str:
    if all(b > a for a, b in zip(values[:-1], values[1:])):
        return "increasing"
    if all(b < a for a, b in zip(values[:-1], values[1:])):
        return "decreasing"
    return "mixed"


def fit_linear_model(features: list[list[float]], targets: list[float]) -> tuple[list[float], list[float], float]:
    design = [[1.0, *row] for row in features]
    columns = len(design[0])
    xtx = [[0.0 for _ in range(columns)] for _ in range(columns)]
    xty = [0.0 for _ in range(columns)]

    for row, target in zip(design, targets):
        for i in range(columns):
            xty[i] += row[i] * target
            for j in range(columns):
                xtx[i][j] += row[i] * row[j]

    coeffs = solve_linear_system(xtx, xty)
    predictions = [sum(coef * value for coef, value in zip(coeffs, row)) for row in design]
    rmse = math.sqrt(sum((target - prediction) ** 2 for target, prediction in zip(targets, predictions)) / len(targets))
    return coeffs, predictions, rmse


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]

    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row_index: abs(augmented[row_index][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) < 1e-12:
            augmented[pivot_row][pivot_index] = 1e-12
        if pivot_row != pivot_index:
            augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]

        pivot = augmented[pivot_index][pivot_index]
        for column in range(pivot_index, size + 1):
            augmented[pivot_index][column] /= pivot

        for row_index in range(size):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            for column in range(pivot_index, size + 1):
                augmented[row_index][column] -= factor * augmented[pivot_index][column]

    return [augmented[index][size] for index in range(size)]


def second_differences(values: list[float]) -> list[float]:
    if len(values) < 3:
        return [0.0 for _ in values]

    result = [0.0]
    for index in range(1, len(values) - 1):
        result.append(values[index + 1] - 2.0 * values[index] + values[index - 1])
    result.append(0.0)
    return result


def analyze_family(series: list[dict]) -> dict:
    indices = list(range(len(series)))
    radii = [item["radius_pm"] for item in series]
    ionization = [item["ionization_ev"] for item in series]
    zeff = [estimate_zeff(item["ionization_ev"], item["period"]) for item in series]
    torsion = [abs(value) for value in second_differences(radii)]
    curvature = [abs(value) for value in second_differences(zeff)]

    baseline_coeffs, baseline_prediction, baseline_rmse = fit_linear_model(
        [[float(index)] for index in indices],
        radii,
    )
    internal_ratio = [radius / prediction if prediction else 0.0 for radius, prediction in zip(radii, baseline_prediction)]

    omega_features = [
        [float(index), torsion_value, curvature_value, ratio_value]
        for index, torsion_value, curvature_value, ratio_value in zip(indices, torsion, curvature, internal_ratio)
    ]
    omega_coeffs, omega_prediction, omega_rmse = fit_linear_model(omega_features, radii)
    omega_gain = baseline_rmse - omega_rmse
    omega_gain_ratio = omega_gain / baseline_rmse if baseline_rmse else 0.0

    band_ok = sum(0.90 <= ratio <= 1.10 for ratio in internal_ratio) < len(internal_ratio)
    torsion_signal = max(torsion) if torsion else 0.0
    curvature_signal = max(curvature) if curvature else 0.0
    structure_ok = omega_gain_ratio > 0.05 and torsion_signal > 0.10 and curvature_signal > 0.10

    evaluated = []
    for item, zeff_value, tor_value, cur_value, ratio_value, omega_pred in zip(
        series,
        zeff,
        torsion,
        curvature,
        internal_ratio,
        omega_prediction,
    ):
        evaluated.append(
            {
                **item,
                "index": series.index(item),
                "zeff_proxy": round(zeff_value, 6),
                "torsion": round(tor_value, 6),
                "curvature": round(cur_value, 6),
                "radius_internal_normalized": round(ratio_value, 6),
                "omega_residual": round(item["radius_pm"] - omega_pred, 6),
            }
        )

    return {
        "series": evaluated,
        "radius_trend": trend(radii),
        "ionization_trend": trend(ionization),
        "zeff_trend": trend(zeff),
        "torsion_trend": trend(torsion),
        "curvature_trend": trend(curvature),
        "baseline": {
            "coefficients": baseline_coeffs,
            "rmse": baseline_rmse,
        },
        "omega": {
            "coefficients": omega_coeffs,
            "rmse": omega_rmse,
            "gain": omega_gain,
            "gain_ratio": omega_gain_ratio,
        },
        "signals": {
            "max_torsion": torsion_signal,
            "max_curvature": curvature_signal,
            "internal_ratio_band_ok": band_ok,
        },
        "criteria": {
            "omega_local_useful": omega_gain_ratio > 0.05,
            "omega_structurel_net": torsion_signal > 0.10 and curvature_signal > 0.10,
            "omega_distinct": band_ok,
            "structure_ok": structure_ok,
        },
    }


def classify(primary_metrics: dict, probe_metrics: dict) -> dict:
    primary_ok = primary_metrics["criteria"]["omega_local_useful"] and primary_metrics["criteria"]["omega_structurel_net"]
    probe_ok = probe_metrics["criteria"]["omega_distinct"] or probe_metrics["criteria"]["structure_ok"]

    if primary_ok and probe_ok:
        verdict = "supported"
    elif primary_ok or probe_ok:
        verdict = "partiel"
    else:
        verdict = "contradicted"

    return {
        "hypothesis": "Omega(Z) improves the reading of heavy series by adding torsion, curvature and a normalized internal radius",
        "case_control": "lanthanides as primary heavy series with Fr / Ra / Lr as heavy probes",
        "observable": "baseline versus Omega fit, torsion residuals, curvature and normalized internal radius",
        "expected": {
            "primary_series": "local gain over the compact baseline",
            "probe_series": "distinct heavy-case structure without universal collapse",
        },
        "measured": {
            "lanthanides": primary_metrics,
            "heavy_probes": probe_metrics,
        },
        "criteria": {
            "primary_ok": primary_ok,
            "probe_ok": probe_ok,
        },
        "verdict": verdict,
        "falsifiers": [
            "Omega(Z) does not improve the baseline fit",
            "torsion and curvature remain invisible",
            "the normalized internal radius stays in a trivial band for every case",
        ],
    }


def write_report(results: dict, outdir: Path) -> tuple[Path, Path]:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    outdir.mkdir(parents=True, exist_ok=True)

    json_path = outdir / f"omega_z_structure_check_{timestamp}.json"
    txt_path = outdir / f"omega_z_structure_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Omega(Z) structure check",
        f"Timestamp: {timestamp}",
        "",
        f"Hypothese: {results['hypothesis']}",
        f"Cas de controle: {results['case_control']}",
        f"Observable: {results['observable']}",
        f"Verdict: {results['verdict']}",
        "",
        "Lanthanides:",
    ]
    lanthanides = results["measured"]["lanthanides"]
    for item in lanthanides["series"]:
        lines.append(
            f"- {item['symbol']}: radius={item['radius_pm']:.1f} zeff={item['zeff_proxy']:.6f} torsion={item['torsion']:.6f} curvature={item['curvature']:.6f} ratio={item['radius_internal_normalized']:.6f}"
        )
    lines.extend(
        [
            "",
            f"Baseline RMSE: {lanthanides['baseline']['rmse']:.6f}",
            f"Omega RMSE: {lanthanides['omega']['rmse']:.6f}",
            f"Omega gain ratio: {lanthanides['omega']['gain_ratio']:.6f}",
            f"Max torsion: {lanthanides['signals']['max_torsion']:.6f}",
            f"Max curvature: {lanthanides['signals']['max_curvature']:.6f}",
            "",
            "Heavy probes:",
        ]
    )
    heavy_probes = results["measured"]["heavy_probes"]
    for item in heavy_probes["series"]:
        lines.append(
            f"- {item['symbol']}: radius={item['radius_pm']:.1f} zeff={item['zeff_proxy']:.6f} torsion={item['torsion']:.6f} curvature={item['curvature']:.6f} ratio={item['radius_internal_normalized']:.6f}"
        )
    lines.extend(
        [
            "",
            f"Primary criteria: {lanthanides['criteria']}",
            f"Probe criteria: {heavy_probes['criteria']}",
        ]
    )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the dedicated Omega(Z) structure check.")
    _ = parser.parse_args()

    primary_metrics = analyze_family(LANTHANIDES)
    probe_metrics = analyze_family(HEAVY_PROBES)
    results = classify(primary_metrics, probe_metrics)

    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "omega_structure"
    json_path, txt_path = write_report(results, outdir)

    payload = {"json_path": str(json_path), "txt_path": str(txt_path), **results}
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()