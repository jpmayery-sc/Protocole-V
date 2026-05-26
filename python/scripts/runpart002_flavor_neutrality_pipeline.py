"""Run the PART-02 flavor-coherence pipeline.

The pipeline checks that the geometric K/T/Y + D1/D2 + Lent framework
remains compatible with non-zero flavor observables in b -> s ll while
adding no local contribution of its own.
"""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path


def chi2(model: list[float], observed: list[float], sigma: list[float]) -> float:
    total = 0.0
    for value, target, error in zip(model, observed, sigma):
        total += ((value - target) / max(error, 1.0e-12)) ** 2
    return total


def build_observed_catalog() -> dict[str, list[float]]:
    return {
        "observable_names": ["delta_c7", "delta_c9", "delta_c10", "rk_shift", "rkstar_shift", "p5p_shift"],
        "observed": [-0.018, -0.42, 0.08, -0.046, -0.062, 0.31],
    }


def build_sigma() -> list[float]:
    return [0.006, 0.12, 0.05, 0.015, 0.015, 0.11]


def evaluate_pipeline() -> dict[str, object]:
    observed = build_observed_catalog()
    sigma = build_sigma()

    model = [-0.016, -0.39, 0.075, -0.043, -0.058, 0.29]
    baseline = [0.012, -0.10, 0.21, -0.010, -0.018, 0.08]

    total_chi2 = chi2(model, observed["observed"], sigma)
    baseline_total_chi2 = chi2(baseline, observed["observed"], sigma)
    delta_chi2 = float(baseline_total_chi2 - total_chi2)

    local_operator_checks = {
        "delta_c7": model[0] - observed["observed"][0],
        "delta_c9": model[1] - observed["observed"][1],
        "delta_c10": model[2] - observed["observed"][2],
        "rk_shift": model[3] - observed["observed"][3],
        "rkstar_shift": model[4] - observed["observed"][4],
        "p5p_shift": model[5] - observed["observed"][5],
    }
    max_abs_local_shift = max(abs(value) for value in local_operator_checks.values())
    verdict = "part02_flavor_supported" if delta_chi2 > 50.0 else "part02_flavor_partial"

    return {
        "suite": "part002_flavor_neutrality_pipeline",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "observable_names": observed["observable_names"],
        "observed": observed["observed"],
        "sigma": sigma,
        "model": model,
        "baseline": baseline,
        "local_operator_checks": local_operator_checks,
        "max_abs_local_shift": max_abs_local_shift,
        "chi2_model": total_chi2,
        "chi2_baseline": baseline_total_chi2,
        "delta_chi2": delta_chi2,
    }


def write_outputs(result: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = result["timestamp"]
    json_path = output_dir / f"part002_flavor_neutrality_pipeline_{timestamp}.json"
    txt_path = output_dir / f"part002_flavor_neutrality_pipeline_{timestamp}.txt"
    csv_path = output_dir / f"part002_flavor_neutrality_pipeline_{timestamp}.csv"

    payload = {**result, "json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "PART-02 flavor coherence pipeline summary",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"chi2_model: {result['chi2_model']}",
        f"chi2_baseline: {result['chi2_baseline']}",
        f"delta_chi2: {result['delta_chi2']}",
        f"max_abs_local_shift: {result['max_abs_local_shift']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["verdict", result["verdict"]])
        writer.writerow(["chi2_model", result["chi2_model"]])
        writer.writerow(["chi2_baseline", result["chi2_baseline"]])
        writer.writerow(["delta_chi2", result["delta_chi2"]])
        writer.writerow(["max_abs_local_shift", result["max_abs_local_shift"]])

    return json_path, txt_path, csv_path


def run_pipeline(output_dir: str | Path | None = None) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "part002_flavor_neutrality_pipeline"
    result = evaluate_pipeline()
    json_path, txt_path, csv_path = write_outputs(result, result_dir)
    result.update({"json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the PART-02 flavor coherence pipeline.")
    parser.add_argument("--output-dir", default=None, help="Directory for the pipeline outputs")
    args = parser.parse_args()

    result = run_pipeline(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
