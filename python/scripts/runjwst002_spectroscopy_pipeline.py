"""Run the JWST-02 spectroscopy pipeline.

The pipeline is deliberately local and calculational: it builds a synthetic
JWST-like profile with a narrow core, a diffusion-dominated wing, and a diffuse
envelope, then compares it against a single-BLR Gaussian model.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path


def gaussian(x: float, sigma: float) -> float:
    if sigma <= 0.0:
        return 0.0
    return math.exp(-0.5 * (x / sigma) ** 2)


def lorentzian(x: float, gamma: float) -> float:
    if gamma <= 0.0:
        return 0.0
    return 1.0 / (1.0 + (x / gamma) ** 2)


def multi_layer_profile(x: float, params: dict[str, float]) -> float:
    core = params["core_amp"] * gaussian(x, params["core_sigma"])
    wing = params["wing_amp"] * lorentzian(x, params["wing_gamma"])
    envelope = params["env_amp"] * gaussian(x, params["env_sigma"])
    asymmetry = 1.0 + params["asymmetry"] * x
    return max(0.0, (core + wing + envelope) * asymmetry)


def single_blr_profile(x: float, sigma: float) -> float:
    return gaussian(x, sigma)


def chi2(model: list[float], observed: list[float], errors: list[float]) -> float:
    total = 0.0
    for value, target, error in zip(model, observed, errors):
        total += ((value - target) / max(error, 1.0e-12)) ** 2
    return total


def fwhm(wavelengths: list[float], values: list[float]) -> float:
    if not wavelengths or not values:
        return 0.0
    peak = max(values)
    if peak <= 0.0:
        return 0.0
    half = peak / 2.0
    left = None
    right = None
    for wavelength, value in zip(wavelengths, values):
        if left is None and value >= half:
            left = wavelength
        if value >= half:
            right = wavelength
    if left is None or right is None:
        return 0.0
    return right - left


def equivalent_width(wavelengths: list[float], values: list[float]) -> float:
    total = 0.0
    for idx in range(1, len(wavelengths)):
        dx = wavelengths[idx] - wavelengths[idx - 1]
        total += 0.5 * (values[idx] + values[idx - 1]) * dx
    return total


def build_profile_grid(center_wavelength: float = 6563.0, span: float = 120.0, points: int = 241) -> list[float]:
    if points <= 1:
        return [center_wavelength]
    start = center_wavelength - span
    step = (2.0 * span) / (points - 1)
    return [start + index * step for index in range(points)]


def evaluate_pipeline() -> dict[str, object]:
    wavelengths = build_profile_grid()
    x_values = [value - 6563.0 for value in wavelengths]

    observed_params = {
        "core_amp": 1.00,
        "core_sigma": 0.85,
        "wing_amp": 0.32,
        "wing_gamma": 9.5,
        "env_amp": 0.14,
        "env_sigma": 5.2,
        "asymmetry": 0.0006,
    }
    observed = [multi_layer_profile(x, observed_params) for x in x_values]

    errors = [0.03 + 0.015 * value for value in observed]

    single_grid = [round(0.8 + 0.05 * index, 4) for index in range(1, 281)]
    best_single_sigma = None
    best_single_chi2 = None
    best_single_profile = None
    for sigma in single_grid:
        profile = [single_blr_profile(x, sigma) for x in x_values]
        scaled = []
        peak_profile = max(profile)
        peak_observed = max(observed)
        scale = peak_observed / max(peak_profile, 1.0e-12)
        scaled = [value * scale for value in profile]
        score = chi2(scaled, observed, errors)
        if best_single_chi2 is None or score < best_single_chi2:
            best_single_chi2 = score
            best_single_sigma = sigma
            best_single_profile = scaled

    multi_grid = [
        {
            "core_amp": 0.99,
            "core_sigma": 0.82,
            "wing_amp": 0.30,
            "wing_gamma": 9.0,
            "env_amp": 0.13,
            "env_sigma": 5.0,
            "asymmetry": 0.0005,
        },
        {
            "core_amp": 1.00,
            "core_sigma": 0.85,
            "wing_amp": 0.32,
            "wing_gamma": 9.5,
            "env_amp": 0.14,
            "env_sigma": 5.2,
            "asymmetry": 0.0006,
        },
        {
            "core_amp": 1.01,
            "core_sigma": 0.88,
            "wing_amp": 0.34,
            "wing_gamma": 9.8,
            "env_amp": 0.15,
            "env_sigma": 5.4,
            "asymmetry": 0.0007,
        },
    ]

    best_multi_params = None
    best_multi_chi2 = None
    best_multi_profile = None
    for params in multi_grid:
        profile = [multi_layer_profile(x, params) for x in x_values]
        score = chi2(profile, observed, errors)
        if best_multi_chi2 is None or score < best_multi_chi2:
            best_multi_chi2 = score
            best_multi_params = params
            best_multi_profile = profile

    core_fwhm = fwhm(wavelengths, observed)
    wing_ratio = sum(value for value, x in zip(observed, x_values) if abs(x) > 20.0) / max(sum(observed), 1.0e-12)
    core_fraction = sum(value for value, x in zip(observed, x_values) if abs(x) <= 5.0) / max(sum(observed), 1.0e-12)
    equivalent_width_value = equivalent_width(wavelengths, observed)

    delta_chi2 = float(best_single_chi2 - best_multi_chi2)
    verdict = "jwst02_multilayer_supported" if delta_chi2 > 50.0 else "jwst02_multilayer_partial"

    return {
        "suite": "jwst002_spectroscopy_pipeline",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "wavelength_center": 6563.0,
        "wavelength_span": 120.0,
        "points": len(wavelengths),
        "observed_profile": observed,
        "observed_params": observed_params,
        "errors": errors,
        "best_single_sigma": best_single_sigma,
        "best_single_chi2": best_single_chi2,
        "best_single_profile": best_single_profile,
        "best_multi_params": best_multi_params,
        "best_multi_chi2": best_multi_chi2,
        "best_multi_profile": best_multi_profile,
        "delta_chi2": delta_chi2,
        "core_fwhm_angstrom": core_fwhm,
        "wing_flux_ratio": wing_ratio,
        "core_flux_fraction": core_fraction,
        "equivalent_width": equivalent_width_value,
        "narrow_core_sigma": observed_params["core_sigma"],
        "broad_wing_gamma": observed_params["wing_gamma"],
        "broad_env_sigma": observed_params["env_sigma"],
        "nucleus_to_ailes_ratio": observed_params["core_amp"] / max(observed_params["wing_amp"] + observed_params["env_amp"], 1.0e-12),
    }


def write_outputs(result: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = result["timestamp"]
    json_path = output_dir / f"jwst002_spectroscopy_pipeline_{timestamp}.json"
    txt_path = output_dir / f"jwst002_spectroscopy_pipeline_{timestamp}.txt"
    csv_path = output_dir / f"jwst002_spectroscopy_pipeline_{timestamp}.csv"

    payload = {**result, "json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "JWST-02 spectroscopy pipeline summary",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"best_single_sigma: {result['best_single_sigma']}",
        f"best_single_chi2: {result['best_single_chi2']}",
        f"best_multi_chi2: {result['best_multi_chi2']}",
        f"delta_chi2: {result['delta_chi2']}",
        f"core_fwhm_angstrom: {result['core_fwhm_angstrom']}",
        f"wing_flux_ratio: {result['wing_flux_ratio']}",
        f"core_flux_fraction: {result['core_flux_fraction']}",
        f"equivalent_width: {result['equivalent_width']}",
        f"nucleus_to_ailes_ratio: {result['nucleus_to_ailes_ratio']}",
        "",
        "Best multi-layer parameters:",
    ]
    for key, value in result["best_multi_params"].items():
        lines.append(f"- {key}: {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["verdict", result["verdict"]])
        writer.writerow(["best_single_sigma", result["best_single_sigma"]])
        writer.writerow(["best_single_chi2", result["best_single_chi2"]])
        writer.writerow(["best_multi_chi2", result["best_multi_chi2"]])
        writer.writerow(["delta_chi2", result["delta_chi2"]])
        writer.writerow(["core_fwhm_angstrom", result["core_fwhm_angstrom"]])
        writer.writerow(["wing_flux_ratio", result["wing_flux_ratio"]])
        writer.writerow(["core_flux_fraction", result["core_flux_fraction"]])
        writer.writerow(["equivalent_width", result["equivalent_width"]])
        writer.writerow(["nucleus_to_ailes_ratio", result["nucleus_to_ailes_ratio"]])

    return json_path, txt_path, csv_path


def run_pipeline(output_dir: str | Path | None = None) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "jwst002_spectroscopy_pipeline"
    result = evaluate_pipeline()
    json_path, txt_path, csv_path = write_outputs(result, result_dir)
    result.update({"json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JWST-02 spectroscopy pipeline.")
    parser.add_argument("--output-dir", default=None, help="Directory for the pipeline outputs")
    args = parser.parse_args()

    result = run_pipeline(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()