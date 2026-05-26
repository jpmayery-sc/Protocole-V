"""Run the JWST-04 galaxy-formation pipeline.

The pipeline homogenizes baryonic assumptions and compares stellar mass,
SFR,
luminosity, and massive-galaxy density against a compact geometric model.
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


def saturating_sfr(redshift: float, s0: float, beta: float, zc: float, gamma: float) -> float:
    numerator = s0 * (1.0 + redshift) ** beta
    denominator = 1.0 + ((1.0 + redshift) / (1.0 + zc)) ** gamma
    return numerator / denominator


def baryonic_luminosity(redshift: float, l0: float, alpha: float, zc: float, delta: float) -> float:
    return l0 * (1.0 + redshift) ** alpha * math.exp(-redshift / zc) * (1.0 + delta * gaussian(redshift, 8.5, 1.1))


def build_observed_catalog() -> dict[str, list[float]]:
    redshift_bins = [6.0, 7.0, 8.0, 9.0, 10.0]
    m_hom = [1.8e9, 2.9e9, 4.0e9, 5.2e9, 6.1e9]
    sfr_hom = [18.0, 27.0, 34.0, 39.0, 42.0]
    l_hom = [1.2e10, 1.55e10, 1.86e10, 2.08e10, 2.25e10]
    n_hom = [0.46, 0.34, 0.25, 0.18, 0.12]
    return {"redshift_bins": redshift_bins, "m_hom": m_hom, "sfr_hom": sfr_hom, "l_hom": l_hom, "n_hom": n_hom}


def build_sigma() -> dict[str, list[float]]:
    return {
        "m_hom": [2.2e8, 2.5e8, 2.8e8, 3.0e8, 3.2e8],
        "sfr_hom": [2.5, 2.8, 3.0, 3.1, 3.2],
        "l_hom": [1.2e9, 1.2e9, 1.3e9, 1.3e9, 1.4e9],
        "n_hom": [0.05, 0.05, 0.04, 0.04, 0.03],
    }


def model_homogenized_catalog(redshift_bins: list[float]) -> dict[str, list[float]]:
    observed = build_observed_catalog()
    sigma = build_sigma()

    best_score: float | None = None
    best_model: dict[str, list[float]] | None = None

    for z_break in (7.0, 7.4, 7.8):
        for alpha1 in (1.1, 1.3, 1.5, 1.7):
            for delta_alpha in (0.5, 0.7, 0.9, 1.1):
                alpha2 = alpha1 - delta_alpha
                for amplitude in (2.0e7, 3.0e7, 4.0e7, 5.0e7, 6.0e7):
                    m_mod = [broken_power_law(z, amplitude, alpha1, alpha2, z_break) for z in redshift_bins]
                    m_score = chi2(m_mod, observed["m_hom"], sigma["m_hom"])

                    for s0 in (2.0, 3.0, 4.0, 5.0, 6.0, 7.0):
                        for beta in (1.0, 1.2, 1.4, 1.6):
                            for zc in (7.0, 7.4, 7.8, 8.2):
                                for gamma in (1.5, 2.0, 2.5, 3.0):
                                    sfr_mod = [saturating_sfr(z, s0, beta, zc, gamma) for z in redshift_bins]
                                    sfr_score = chi2(sfr_mod, observed["sfr_hom"], sigma["sfr_hom"])

                                    for l0 in (1.0e10, 1.2e10, 1.4e10, 1.6e10):
                                        for alpha in (0.1, 0.2, 0.3, 0.4):
                                            for lzc in (6.0, 6.5, 7.0):
                                                for delta in (0.02, 0.05, 0.08, 0.11):
                                                    l_mod = [baryonic_luminosity(z, l0, alpha, lzc, delta) for z in redshift_bins]
                                                    n_mod = [0.55 * math.exp(-0.28 * (z - 6.0)) + 0.06 * gaussian(z, 8.0, 0.7) for z in redshift_bins]
                                                    score = (
                                                        m_score
                                                        + sfr_score
                                                        + chi2(l_mod, observed["l_hom"], sigma["l_hom"])
                                                        + chi2(n_mod, observed["n_hom"], sigma["n_hom"])
                                                    )
                                                    if best_score is None or score < best_score:
                                                        best_score = score
                                                        best_model = {
                                                            "m_mod": m_mod,
                                                            "sfr_mod": sfr_mod,
                                                            "l_mod": l_mod,
                                                            "n_mod": n_mod,
                                                            "z_break": z_break,
                                                            "alpha1": alpha1,
                                                            "alpha2": alpha2,
                                                            "s0": s0,
                                                            "beta": beta,
                                                            "zc": zc,
                                                            "gamma": gamma,
                                                            "l0": l0,
                                                            "alpha_l": alpha,
                                                            "lzc": lzc,
                                                            "delta": delta,
                                                        }

    assert best_model is not None
    return best_model


def simple_burst_model(redshift_bins: list[float]) -> dict[str, list[float]]:
    m_mod = []
    sfr_mod = []
    l_mod = []
    n_mod = []
    for z in redshift_bins:
        m_mod.append(3.0e8 * (1.0 + z) ** 2.9)
        sfr_mod.append(12.0 * (1.0 + z) ** 1.9)
        l_mod.append(8.0e9 * (1.0 + z) ** 0.8)
        n_mod.append(0.95 * math.exp(-0.08 * (z - 6.0)))
    return {"m_mod": m_mod, "sfr_mod": sfr_mod, "l_mod": l_mod, "n_mod": n_mod}


def evaluate_pipeline() -> dict[str, object]:
    observed = build_observed_catalog()
    sigma = build_sigma()
    redshift_bins = observed["redshift_bins"]

    model = model_homogenized_catalog(redshift_bins)
    baseline = simple_burst_model(redshift_bins)

    chi2_m = chi2(model["m_mod"], observed["m_hom"], sigma["m_hom"])
    chi2_sfr = chi2(model["sfr_mod"], observed["sfr_hom"], sigma["sfr_hom"])
    chi2_l = chi2(model["l_mod"], observed["l_hom"], sigma["l_hom"])
    chi2_n = chi2(model["n_mod"], observed["n_hom"], sigma["n_hom"])

    baseline_chi2_m = chi2(baseline["m_mod"], observed["m_hom"], sigma["m_hom"])
    baseline_chi2_sfr = chi2(baseline["sfr_mod"], observed["sfr_hom"], sigma["sfr_hom"])
    baseline_chi2_l = chi2(baseline["l_mod"], observed["l_hom"], sigma["l_hom"])
    baseline_chi2_n = chi2(baseline["n_mod"], observed["n_hom"], sigma["n_hom"])

    total_chi2 = chi2_m + chi2_sfr + chi2_l + chi2_n
    baseline_total_chi2 = baseline_chi2_m + baseline_chi2_sfr + baseline_chi2_l + baseline_chi2_n
    delta_chi2 = float(baseline_total_chi2 - total_chi2)
    verdict = "jwst04_homogenized_supported" if delta_chi2 > 50.0 else "jwst04_homogenized_partial"

    return {
        "suite": "jwst004_galaxy_formation_pipeline",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "redshift_bins": redshift_bins,
        "observed": observed,
        "sigma": sigma,
        "model": model,
        "baseline": baseline,
        "chi2_m": chi2_m,
        "chi2_sfr": chi2_sfr,
        "chi2_l": chi2_l,
        "chi2_n": chi2_n,
        "baseline_chi2_m": baseline_chi2_m,
        "baseline_chi2_sfr": baseline_chi2_sfr,
        "baseline_chi2_l": baseline_chi2_l,
        "baseline_chi2_n": baseline_chi2_n,
        "total_chi2": total_chi2,
        "baseline_total_chi2": baseline_total_chi2,
        "delta_chi2": delta_chi2,
        "mean_m_hom": sum(observed["m_hom"]) / len(observed["m_hom"]),
        "mean_sfr_hom": sum(observed["sfr_hom"]) / len(observed["sfr_hom"]),
        "mean_l_hom": sum(observed["l_hom"]) / len(observed["l_hom"]),
        "mean_n_hom": sum(observed["n_hom"]) / len(observed["n_hom"]),
    }


def write_outputs(result: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = result["timestamp"]
    json_path = output_dir / f"jwst004_galaxy_formation_pipeline_{timestamp}.json"
    txt_path = output_dir / f"jwst004_galaxy_formation_pipeline_{timestamp}.txt"
    csv_path = output_dir / f"jwst004_galaxy_formation_pipeline_{timestamp}.csv"

    payload = {**result, "json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "JWST-04 galaxy formation pipeline summary",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"chi2_m: {result['chi2_m']}",
        f"chi2_sfr: {result['chi2_sfr']}",
        f"chi2_l: {result['chi2_l']}",
        f"chi2_n: {result['chi2_n']}",
        f"baseline_total_chi2: {result['baseline_total_chi2']}",
        f"total_chi2: {result['total_chi2']}",
        f"delta_chi2: {result['delta_chi2']}",
        f"mean_m_hom: {result['mean_m_hom']}",
        f"mean_sfr_hom: {result['mean_sfr_hom']}",
        f"mean_l_hom: {result['mean_l_hom']}",
        f"mean_n_hom: {result['mean_n_hom']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["verdict", result["verdict"]])
        writer.writerow(["chi2_m", result["chi2_m"]])
        writer.writerow(["chi2_sfr", result["chi2_sfr"]])
        writer.writerow(["chi2_l", result["chi2_l"]])
        writer.writerow(["chi2_n", result["chi2_n"]])
        writer.writerow(["baseline_total_chi2", result["baseline_total_chi2"]])
        writer.writerow(["total_chi2", result["total_chi2"]])
        writer.writerow(["delta_chi2", result["delta_chi2"]])

    return json_path, txt_path, csv_path


def run_pipeline(output_dir: str | Path | None = None) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "jwst004_galaxy_formation_pipeline"
    result = evaluate_pipeline()
    json_path, txt_path, csv_path = write_outputs(result, result_dir)
    result.update({"json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the JWST-04 galaxy formation pipeline.")
    parser.add_argument("--output-dir", default=None, help="Directory for the pipeline outputs")
    args = parser.parse_args()

    result = run_pipeline(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()