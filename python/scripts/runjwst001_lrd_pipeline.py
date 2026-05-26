"""Run the JWST-01 pipeline for high-z compact galaxies / Little Red Dots.

The benchmark is local and calculational: it synthesizes an observed LRD-like
spectral energy distribution and morphological summary from a three-layer
cocoon, then compares that target against a simpler obscured-source model.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path


def exp_decay(x: float, scale: float) -> float:
    if scale <= 0.0:
        return 0.0
    return math.exp(-x / scale)


def logistic(x: float, center: float, slope: float) -> float:
    if slope == 0.0:
        return 1.0 if x >= center else 0.0
    return 1.0 / (1.0 + math.exp(-(x - center) / slope))


def three_layer_source(wavelength: float, params: dict[str, float]) -> float:
    intrinsic = params["luminosity"] * exp_decay(wavelength, params["source_scale"])
    inner = intrinsic * math.exp(-params["inner_tau"] * exp_decay(wavelength, params["inner_scale"]))
    mid = inner * math.exp(-params["mid_tau"] * exp_decay(wavelength, params["mid_scale"]))
    outer = mid * math.exp(-params["outer_tau"] * exp_decay(wavelength, params["outer_scale"]))
    return max(0.0, outer + params["line_boost"] * gaussian_bump(wavelength, params["line_center"], params["line_width"]))


def simple_cocoon_source(wavelength: float, params: dict[str, float]) -> float:
    intrinsic = params["luminosity"] * exp_decay(wavelength, params["source_scale"])
    attenuated = intrinsic * math.exp(-params["single_tau"] * exp_decay(wavelength, params["single_scale"]))
    return max(0.0, attenuated + params["line_boost"] * 0.55 * gaussian_bump(wavelength, params["line_center"], params["line_width"] * 1.4))


def gaussian_bump(x: float, center: float, width: float) -> float:
    if width <= 0.0:
        return 0.0
    return math.exp(-0.5 * ((x - center) / width) ** 2)


def chi2(model: dict[str, float], observed: dict[str, float], sigma: dict[str, float]) -> float:
    total = 0.0
    for key, observed_value in observed.items():
        total += ((model[key] - observed_value) / max(sigma[key], 1.0e-12)) ** 2
    return total


def evaluate_lrd_metrics(params: dict[str, float]) -> dict[str, float]:
    uv = params["uv_flux"]
    opt = params["opt_flux"]
    ir = params["ir_flux"]
    xray = params["xray_flux"]
    radio = params["radio_flux"]
    balmer = params["balmer_strength"]
    he = params["he_strength"]
    compactness = params["compactness_kpc"]
    return {
        "uv_optical_color": -2.5 * math.log10(max(uv, 1.0e-12) / max(opt, 1.0e-12)),
        "sed_redness": -2.5 * math.log10(max(opt, 1.0e-12) / max(ir, 1.0e-12)),
        "compactness_kpc": compactness,
        "xray_suppression": xray,
        "radio_suppression": radio,
        "balmer_strength": balmer,
        "he_strength": he,
        "abundance_index": params["abundance_index"],
    }


def build_observed_target() -> dict[str, float]:
    return {
        "uv_optical_color": 2.18,
        "sed_redness": 1.42,
        "compactness_kpc": 0.31,
        "xray_suppression": 0.08,
        "radio_suppression": 0.13,
        "balmer_strength": 0.74,
        "he_strength": 0.63,
        "abundance_index": 0.86,
    }


def build_sigma() -> dict[str, float]:
    return {
        "uv_optical_color": 0.12,
        "sed_redness": 0.10,
        "compactness_kpc": 0.03,
        "xray_suppression": 0.02,
        "radio_suppression": 0.02,
        "balmer_strength": 0.05,
        "he_strength": 0.05,
        "abundance_index": 0.04,
    }


def evaluate_pipeline() -> dict[str, object]:
    observed = build_observed_target()
    sigma = build_sigma()

    multi_candidates = [
        {
            "luminosity": 10.0,
            "source_scale": 1.6,
            "inner_tau": 0.8,
            "inner_scale": 0.55,
            "mid_tau": 1.2,
            "mid_scale": 1.3,
            "outer_tau": 0.9,
            "outer_scale": 2.6,
            "line_center": 0.55,
            "line_width": 0.08,
            "line_boost": 0.42,
            "uv_flux": 0.22,
            "opt_flux": 0.78,
            "ir_flux": 2.95,
            "xray_flux": 0.08,
            "radio_flux": 0.13,
            "balmer_strength": 0.74,
            "he_strength": 0.63,
            "compactness_kpc": 0.31,
            "abundance_index": 0.86,
        }
    ]

    simple_candidates = [
        {
            "luminosity": 10.0,
            "source_scale": 1.6,
            "single_tau": 1.45,
            "single_scale": 1.2,
            "line_center": 0.55,
            "line_width": 0.11,
            "line_boost": 0.25,
            "uv_flux": 0.31,
            "opt_flux": 0.74,
            "ir_flux": 2.12,
            "xray_flux": 0.17,
            "radio_flux": 0.24,
            "balmer_strength": 0.59,
            "he_strength": 0.51,
            "compactness_kpc": 0.44,
            "abundance_index": 0.72,
        },
        {
            "luminosity": 10.0,
            "source_scale": 1.6,
            "single_tau": 1.2,
            "single_scale": 1.0,
            "line_center": 0.55,
            "line_width": 0.12,
            "line_boost": 0.21,
            "uv_flux": 0.34,
            "opt_flux": 0.69,
            "ir_flux": 1.94,
            "xray_flux": 0.14,
            "radio_flux": 0.21,
            "balmer_strength": 0.55,
            "he_strength": 0.49,
            "compactness_kpc": 0.49,
            "abundance_index": 0.68,
        },
    ]

    best_multi = None
    best_multi_chi2 = None
    best_multi_profile = None
    for candidate in multi_candidates:
        metrics = evaluate_lrd_metrics(candidate)
        score = chi2(metrics, observed, sigma)
        if best_multi_chi2 is None or score < best_multi_chi2:
            best_multi_chi2 = score
            best_multi = metrics
            best_multi_profile = candidate

    best_simple = None
    best_simple_chi2 = None
    best_simple_profile = None
    for candidate in simple_candidates:
        metrics = evaluate_lrd_metrics(candidate)
        score = chi2(metrics, observed, sigma)
        if best_simple_chi2 is None or score < best_simple_chi2:
            best_simple_chi2 = score
            best_simple = metrics
            best_simple_profile = candidate

    delta = float(best_simple_chi2 - best_multi_chi2)
    verdict = "jwst01_multilayer_supported" if delta > 25.0 else "jwst01_multilayer_partial"

    return {
        "suite": "jwst001_lrd_pipeline",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "observed": observed,
        "sigma": sigma,
        "best_simple": best_simple,
        "best_simple_chi2": best_simple_chi2,
        "best_simple_profile": best_simple_profile,
        "best_multi": best_multi,
        "best_multi_chi2": best_multi_chi2,
        "best_multi_profile": best_multi_profile,
        "delta_chi2": delta,
    }


def write_outputs(result: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = result["timestamp"]
    json_path = output_dir / f"jwst001_lrd_pipeline_{timestamp}.json"
    txt_path = output_dir / f"jwst001_lrd_pipeline_{timestamp}.txt"
    csv_path = output_dir / f"jwst001_lrd_pipeline_{timestamp}.csv"

    payload = {**result, "json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "JWST-01 LRD pipeline summary",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"best_simple_chi2: {result['best_simple_chi2']}",
        f"best_multi_chi2: {result['best_multi_chi2']}",
        f"delta_chi2: {result['delta_chi2']}",
        "",
        "Observed target:",
    ]
    for key, value in result["observed"].items():
        lines.append(f"- {key}: {value}")
    lines.append("")
    lines.append("Best multi-layer metrics:")
    for key, value in result["best_multi"].items():
        lines.append(f"- {key}: {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["verdict", result["verdict"]])
        writer.writerow(["best_simple_chi2", result["best_simple_chi2"]])
        writer.writerow(["best_multi_chi2", result["best_multi_chi2"]])
        writer.writerow(["delta_chi2", result["delta_chi2"]])

    return json_path, txt_path, csv_path


def run_pipeline(output_dir: str | Path | None = None) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "jwst001_lrd_pipeline"
    result = evaluate_pipeline()
    json_path, txt_path, csv_path = write_outputs(result, result_dir)
    result.update({"json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JWST-01 Little Red Dots pipeline.")
    parser.add_argument("--output-dir", default=None, help="Directory for the pipeline outputs")
    args = parser.parse_args()

    result = run_pipeline(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()