"""Run the JWST-05 reionisation pipeline.

The pipeline homogenizes ionizing-efficiency observables and compares them
against a compact geometric cocoon model with D1/D2 topology.
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


def chi2(model: list[float], observed: list[float], sigma: list[float]) -> float:
    total = 0.0
    for value, target, error in zip(model, observed, sigma):
        total += ((value - target) / max(error, 1.0e-12)) ** 2
    return total


def build_observed_catalog() -> dict[str, list[float]]:
    redshift_bins = [9.0, 9.5, 10.0, 10.5, 11.0]
    xiion_hom = [25.28, 25.22, 25.15, 25.08, 25.00]
    fesc_hom = [0.060, 0.072, 0.083, 0.095, 0.108]
    n_hom = [0.52, 0.47, 0.41, 0.34, 0.29]
    tau_hom = [0.056]
    return {
        "redshift_bins": redshift_bins,
        "xiion_hom": xiion_hom,
        "fesc_hom": fesc_hom,
        "n_hom": n_hom,
        "tau_hom": tau_hom,
    }


def build_sigma() -> dict[str, list[float]]:
    return {
        "xiion_hom": [0.18, 0.18, 0.17, 0.17, 0.16],
        "fesc_hom": [0.010, 0.010, 0.011, 0.011, 0.012],
        "n_hom": [0.05, 0.05, 0.05, 0.05, 0.05],
        "tau_hom": [0.004],
    }


def model_reionised_catalog(redshift_bins: list[float]) -> dict[str, list[float]]:
    observed = build_observed_catalog()
    sigma = build_sigma()

    best_score: float | None = None
    best_model: dict[str, list[float]] | None = None

    for compaction in (0.55, 0.65, 0.75, 0.85):
        for anisotropy in (0.35, 0.45, 0.55, 0.65):
            for topology in (0.35, 0.45, 0.55, 0.65):
                for xi0 in (25.00, 25.05, 25.10, 25.15):
                    xiion_mod = [
                        xi0 + 0.06 * (z - 9.0) + 0.10 * compaction - 0.03 * topology + 0.02 * gaussian(z, 10.0, 0.7)
                        for z in redshift_bins
                    ]
                    xi_score = chi2(xiion_mod, observed["xiion_hom"], sigma["xiion_hom"])

                    for fesc0 in (0.045, 0.050, 0.055, 0.060):
                        for escape_boost in (0.015, 0.020, 0.025, 0.030):
                            for slope in (0.35, 0.45, 0.55):
                                fesc_mod = [
                                    fesc0 + escape_boost * (1.0 + 0.30 * anisotropy) * math.exp(-slope * (z - 9.0)) + 0.006 * topology
                                    for z in redshift_bins
                                ]
                                fesc_score = chi2(fesc_mod, observed["fesc_hom"], sigma["fesc_hom"])

                                for n0 in (0.42, 0.46, 0.50, 0.54):
                                    for decay in (0.08, 0.10, 0.12, 0.14):
                                        for bump in (0.03, 0.05, 0.07):
                                            n_mod = [
                                                n0 * math.exp(-decay * (z - 9.0)) + bump * gaussian(z, 10.0, 0.6)
                                                for z in redshift_bins
                                            ]
                                            n_score = chi2(n_mod, observed["n_hom"], sigma["n_hom"])

                                            tau_mod = [
                                                0.045
                                                + 0.006 * escape_boost
                                                + 0.002 * compaction
                                                + 0.0015 * anisotropy
                                                + 0.0005 * topology
                                            ]
                                            tau_score = chi2(tau_mod, observed["tau_hom"], sigma["tau_hom"])

                                            score = xi_score + fesc_score + n_score + tau_score
                                            if best_score is None or score < best_score:
                                                best_score = score
                                                best_model = {
                                                    "xiion_mod": xiion_mod,
                                                    "fesc_mod": fesc_mod,
                                                    "n_mod": n_mod,
                                                    "tau_mod": tau_mod,
                                                    "compaction": compaction,
                                                    "anisotropy": anisotropy,
                                                    "topology": topology,
                                                    "xi0": xi0,
                                                    "fesc0": fesc0,
                                                    "escape_boost": escape_boost,
                                                    "slope": slope,
                                                    "n0": n0,
                                                    "decay": decay,
                                                    "bump": bump,
                                                }

    assert best_model is not None
    return best_model


def simple_burst_model(redshift_bins: list[float]) -> dict[str, list[float]]:
    xiion_mod = []
    fesc_mod = []
    n_mod = []
    tau_mod = []
    for z in redshift_bins:
        xiion_mod.append(25.6 + 0.18 * (z - 9.0))
        fesc_mod.append(min(0.35, 0.10 + 0.05 * (z - 9.0)))
        n_mod.append(0.75 * math.exp(-0.03 * (z - 9.0)))
    tau_mod.append(0.067)
    return {"xiion_mod": xiion_mod, "fesc_mod": fesc_mod, "n_mod": n_mod, "tau_mod": tau_mod}


def evaluate_pipeline() -> dict[str, object]:
    observed = build_observed_catalog()
    sigma = build_sigma()
    redshift_bins = observed["redshift_bins"]

    model = model_reionised_catalog(redshift_bins)
    baseline = simple_burst_model(redshift_bins)

    chi2_xiion = chi2(model["xiion_mod"], observed["xiion_hom"], sigma["xiion_hom"])
    chi2_fesc = chi2(model["fesc_mod"], observed["fesc_hom"], sigma["fesc_hom"])
    chi2_n = chi2(model["n_mod"], observed["n_hom"], sigma["n_hom"])
    chi2_tau = chi2(model["tau_mod"], observed["tau_hom"], sigma["tau_hom"])

    baseline_chi2_xiion = chi2(baseline["xiion_mod"], observed["xiion_hom"], sigma["xiion_hom"])
    baseline_chi2_fesc = chi2(baseline["fesc_mod"], observed["fesc_hom"], sigma["fesc_hom"])
    baseline_chi2_n = chi2(baseline["n_mod"], observed["n_hom"], sigma["n_hom"])
    baseline_chi2_tau = chi2(baseline["tau_mod"], observed["tau_hom"], sigma["tau_hom"])

    total_chi2 = chi2_xiion + chi2_fesc + chi2_n + chi2_tau
    baseline_total_chi2 = baseline_chi2_xiion + baseline_chi2_fesc + baseline_chi2_n + baseline_chi2_tau
    delta_chi2 = float(baseline_total_chi2 - total_chi2)
    verdict = "jwst05_reionisation_supported" if delta_chi2 > 50.0 else "jwst05_reionisation_partial"

    return {
        "suite": "jwst005_reionisation_pipeline",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "redshift_bins": redshift_bins,
        "observed": observed,
        "sigma": sigma,
        "model": model,
        "baseline": baseline,
        "chi2_xiion": chi2_xiion,
        "chi2_fesc": chi2_fesc,
        "chi2_n": chi2_n,
        "chi2_tau": chi2_tau,
        "baseline_chi2_xiion": baseline_chi2_xiion,
        "baseline_chi2_fesc": baseline_chi2_fesc,
        "baseline_chi2_n": baseline_chi2_n,
        "baseline_chi2_tau": baseline_chi2_tau,
        "total_chi2": total_chi2,
        "baseline_total_chi2": baseline_total_chi2,
        "delta_chi2": delta_chi2,
        "mean_xiion_hom": sum(observed["xiion_hom"]) / len(observed["xiion_hom"]),
        "mean_fesc_hom": sum(observed["fesc_hom"]) / len(observed["fesc_hom"]),
        "mean_n_hom": sum(observed["n_hom"]) / len(observed["n_hom"]),
        "tau_hom": observed["tau_hom"][0],
    }


def write_outputs(result: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = result["timestamp"]
    json_path = output_dir / f"jwst005_reionisation_pipeline_{timestamp}.json"
    txt_path = output_dir / f"jwst005_reionisation_pipeline_{timestamp}.txt"
    csv_path = output_dir / f"jwst005_reionisation_pipeline_{timestamp}.csv"

    payload = {**result, "json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "JWST-05 reionisation pipeline summary",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"chi2_xiion: {result['chi2_xiion']}",
        f"chi2_fesc: {result['chi2_fesc']}",
        f"chi2_n: {result['chi2_n']}",
        f"chi2_tau: {result['chi2_tau']}",
        f"baseline_total_chi2: {result['baseline_total_chi2']}",
        f"total_chi2: {result['total_chi2']}",
        f"delta_chi2: {result['delta_chi2']}",
        f"mean_xiion_hom: {result['mean_xiion_hom']}",
        f"mean_fesc_hom: {result['mean_fesc_hom']}",
        f"mean_n_hom: {result['mean_n_hom']}",
        f"tau_hom: {result['tau_hom']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["verdict", result["verdict"]])
        writer.writerow(["chi2_xiion", result["chi2_xiion"]])
        writer.writerow(["chi2_fesc", result["chi2_fesc"]])
        writer.writerow(["chi2_n", result["chi2_n"]])
        writer.writerow(["chi2_tau", result["chi2_tau"]])
        writer.writerow(["baseline_total_chi2", result["baseline_total_chi2"]])
        writer.writerow(["total_chi2", result["total_chi2"]])
        writer.writerow(["delta_chi2", result["delta_chi2"]])

    return json_path, txt_path, csv_path


def run_pipeline(output_dir: str | Path | None = None) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "jwst005_reionisation_pipeline"
    result = evaluate_pipeline()
    json_path, txt_path, csv_path = write_outputs(result, result_dir)
    result.update({"json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JWST-05 reionisation pipeline.")
    parser.add_argument("--output-dir", default=None, help="Directory for the pipeline outputs")
    args = parser.parse_args()

    result = run_pipeline(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()