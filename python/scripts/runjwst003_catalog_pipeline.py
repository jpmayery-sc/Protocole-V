"""Run the JWST-03 catalog pipeline.

The pipeline homogenizes a synthetic JWST catalog and compares number densities
and AGN fractions against a simpler selection-biased baseline.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path


def gaussian(x: float, center: float, sigma: float) -> float:
    if sigma <= 0.0:
        return 0.0
    return math.exp(-0.5 * ((x - center) / sigma) ** 2)


def logistic(x: float, center: float, slope: float) -> float:
    if slope == 0.0:
        return 1.0 if x >= center else 0.0
    return 1.0 / (1.0 + math.exp(-(x - center) / slope))


def chi2(model: list[float], observed: list[float], sigma: list[float]) -> float:
    total = 0.0
    for value, target, error in zip(model, observed, sigma):
        total += ((value - target) / max(error, 1.0e-12)) ** 2
    return total


def broken_power_law(redshift: float, amplitude: float, alpha1: float, alpha2: float, z_break: float) -> float:
    if redshift <= z_break:
        return amplitude * (1.0 + redshift) ** alpha1
    return amplitude * (1.0 + z_break) ** (alpha1 - alpha2) * (1.0 + redshift) ** alpha2


def logistic_saturated_agn(redshift: float, f0: float, beta: float, zc: float, gamma: float) -> float:
    base = f0 * (1.0 + redshift) ** beta
    cutoff = 1.0 + ((1.0 + redshift) / (1.0 + zc)) ** gamma
    return max(0.0, min(0.45, base / cutoff))


def build_observed_catalog() -> dict[str, list[float]]:
    redshift_bins = [0.5 + 0.5 * index for index in range(10)]
    n_hom = [18.0, 22.0, 27.5, 31.0, 29.0, 24.0, 20.0, 16.5, 13.0, 10.5]
    f_agn = [0.11, 0.13, 0.16, 0.20, 0.23, 0.24, 0.22, 0.19, 0.16, 0.14]
    return {"redshift_bins": redshift_bins, "n_hom": n_hom, "f_agn": f_agn}


def build_sigma() -> dict[str, list[float]]:
    return {
        "n_hom": [1.8, 1.9, 2.0, 2.1, 2.0, 1.9, 1.8, 1.7, 1.6, 1.5],
        "f_agn": [0.025, 0.025, 0.026, 0.027, 0.027, 0.027, 0.026, 0.025, 0.025, 0.024],
    }


def model_homogenized_catalog(redshift_bins: list[float]) -> dict[str, list[float]]:
    observed = build_observed_catalog()
    sigma = build_sigma()

    best_n_mod: list[float] | None = None
    best_f_agn_mod: list[float] | None = None
    best_score: float | None = None

    for z_break in (2.0, 2.2, 2.4, 2.6):
        for alpha1 in (0.8, 1.0, 1.2, 1.4, 1.6, 1.8):
            for delta_alpha in (1.0, 1.4, 1.8, 2.2):
                alpha2 = alpha1 - delta_alpha
                for amplitude in (10.0, 11.0, 12.0, 13.0, 14.0, 15.0):
                    n_mod = [broken_power_law(z, amplitude, alpha1, alpha2, z_break) for z in redshift_bins]
                    n_score = chi2(n_mod, observed["n_hom"], sigma["n_hom"])

                    for f0 in (0.12, 0.14, 0.16, 0.18, 0.20):
                        for beta in (0.2, 0.3, 0.4, 0.5):
                            for zc in (2.4, 2.6, 2.8, 3.0, 3.2):
                                for gamma in (1.0, 1.5, 2.0, 2.5, 3.0):
                                    f_agn_mod = [logistic_saturated_agn(z, f0, beta, zc, gamma) for z in redshift_bins]
                                    score = n_score + chi2(f_agn_mod, observed["f_agn"], sigma["f_agn"])
                                    if best_score is None or score < best_score:
                                        best_score = score
                                        best_n_mod = n_mod
                                        best_f_agn_mod = f_agn_mod

    assert best_n_mod is not None and best_f_agn_mod is not None
    return {"n_mod": best_n_mod, "f_agn_mod": best_f_agn_mod}


def simple_selection_biased_model(redshift_bins: list[float]) -> dict[str, list[float]]:
    n_mod = []
    f_agn_mod = []
    for z in redshift_bins:
        density = 7.0 + 15.0 * gaussian(z, 2.8, 1.8) + 2.0 * gaussian(z, 5.8, 2.0)
        agn_fraction = 0.06 + 0.12 * logistic(z, 2.8, 1.2)
        n_mod.append(density)
        f_agn_mod.append(max(0.0, min(0.35, agn_fraction)))
    return {"n_mod": n_mod, "f_agn_mod": f_agn_mod}


def evaluate_pipeline() -> dict[str, object]:
    observed = build_observed_catalog()
    sigma = build_sigma()
    redshift_bins = observed["redshift_bins"]

    model = model_homogenized_catalog(redshift_bins)
    baseline = simple_selection_biased_model(redshift_bins)

    chi2_n = chi2(model["n_mod"], observed["n_hom"], sigma["n_hom"])
    chi2_agn = chi2(model["f_agn_mod"], observed["f_agn"], sigma["f_agn"])
    baseline_chi2_n = chi2(baseline["n_mod"], observed["n_hom"], sigma["n_hom"])
    baseline_chi2_agn = chi2(baseline["f_agn_mod"], observed["f_agn"], sigma["f_agn"])

    delta_chi2 = float((baseline_chi2_n + baseline_chi2_agn) - (chi2_n + chi2_agn))
    verdict = "jwst03_homogenized_supported" if delta_chi2 > 20.0 else "jwst03_homogenized_partial"

    return {
        "suite": "jwst003_catalog_pipeline",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "redshift_bins": redshift_bins,
        "observed": observed,
        "sigma": sigma,
        "model": model,
        "baseline": baseline,
        "chi2_n": chi2_n,
        "chi2_agn": chi2_agn,
        "baseline_chi2_n": baseline_chi2_n,
        "baseline_chi2_agn": baseline_chi2_agn,
        "delta_chi2": delta_chi2,
        "mean_n_hom": sum(observed["n_hom"]) / len(observed["n_hom"]),
        "mean_f_agn": sum(observed["f_agn"]) / len(observed["f_agn"]),
    }


def write_outputs(result: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = result["timestamp"]
    json_path = output_dir / f"jwst003_catalog_pipeline_{timestamp}.json"
    txt_path = output_dir / f"jwst003_catalog_pipeline_{timestamp}.txt"
    csv_path = output_dir / f"jwst003_catalog_pipeline_{timestamp}.csv"

    payload = {**result, "json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "JWST-03 catalog pipeline summary",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"chi2_n: {result['chi2_n']}",
        f"chi2_agn: {result['chi2_agn']}",
        f"baseline_chi2_n: {result['baseline_chi2_n']}",
        f"baseline_chi2_agn: {result['baseline_chi2_agn']}",
        f"delta_chi2: {result['delta_chi2']}",
        f"mean_n_hom: {result['mean_n_hom']}",
        f"mean_f_agn: {result['mean_f_agn']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["verdict", result["verdict"]])
        writer.writerow(["chi2_n", result["chi2_n"]])
        writer.writerow(["chi2_agn", result["chi2_agn"]])
        writer.writerow(["baseline_chi2_n", result["baseline_chi2_n"]])
        writer.writerow(["baseline_chi2_agn", result["baseline_chi2_agn"]])
        writer.writerow(["delta_chi2", result["delta_chi2"]])

    return json_path, txt_path, csv_path


def run_pipeline(output_dir: str | Path | None = None) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "jwst003_catalog_pipeline"
    result = evaluate_pipeline()
    json_path, txt_path, csv_path = write_outputs(result, result_dir)
    result.update({"json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JWST-03 catalog pipeline.")
    parser.add_argument("--output-dir", default=None, help="Directory for the pipeline outputs")
    args = parser.parse_args()

    result = run_pipeline(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()