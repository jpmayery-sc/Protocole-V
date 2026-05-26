"""Check the V7-ELEC multi-order electron response."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from alphatorsionorder_check import evaluate_torsion_order


EXTRA_ORDERS = [5, 6, 7]
MAX_RMSE_RATIO = 0.10
MIN_FLOOR = 1.0e-06


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fit_power_law(ns: list[float], kappas: list[float]) -> dict:
    log_n = [math.log(value) for value in ns]
    log_k = [math.log(value) for value in kappas]
    mean_n = sum(log_n) / len(log_n)
    mean_k = sum(log_k) / len(log_k)
    numerator = sum((x - mean_n) * (y - mean_k) for x, y in zip(log_n, log_k))
    denominator = sum((x - mean_n) ** 2 for x in log_n)
    slope = numerator / denominator
    intercept = mean_k - slope * mean_n
    exponent = -slope
    predicted = [math.exp(intercept + slope * x) for x in log_n]
    rmse = math.sqrt(sum((pred - actual) ** 2 for pred, actual in zip(predicted, kappas)) / len(kappas))
    mean_kappa = sum(kappas) / len(kappas)
    relative_rmse = rmse / mean_kappa if mean_kappa else float("inf")
    amplitude = math.exp(intercept)
    return {
        "slope": slope,
        "intercept": intercept,
        "exponent": exponent,
        "amplitude": amplitude,
        "predicted": predicted,
        "rmse": rmse,
        "relative_rmse": relative_rmse,
    }


def evaluate_electron_response() -> dict:
    torsion = evaluate_torsion_order()
    base_ns = [float(case["n"]) for case in torsion["cases"]]
    base_kappas = [float(case["kappa_n"]) for case in torsion["cases"]]
    fit = fit_power_law(base_ns, base_kappas)

    extrapolated = []
    for n_value in EXTRA_ORDERS:
        kappa_value = fit["amplitude"] * (float(n_value) ** (-fit["exponent"]))
        extrapolated.append({"n": float(n_value), "kappa": kappa_value})

    full_sequence = [*base_kappas, *[entry["kappa"] for entry in extrapolated]]
    monotone_ok = all(later < earlier for earlier, later in zip(full_sequence, full_sequence[1:]))
    positive_ok = all(value > 0.0 for value in full_sequence)
    saturation_absent_ok = full_sequence[-1] > MIN_FLOOR and full_sequence[-1] < full_sequence[0]
    critical_floor_ok = full_sequence[-1] > MIN_FLOOR
    fit_quality_ok = fit["relative_rmse"] < MAX_RMSE_RATIO
    verdict = "conforme" if (
        monotone_ok
        and positive_ok
        and saturation_absent_ok
        and critical_floor_ok
        and fit_quality_ok
        and torsion["verdict"] == "conforme"
    ) else "rejette"

    return {
        "base_ns": base_ns,
        "base_kappas": base_kappas,
        "extrapolated": extrapolated,
        "fit": fit,
        "monotone_ok": monotone_ok,
        "positive_ok": positive_ok,
        "saturation_absent_ok": saturation_absent_ok,
        "critical_floor_ok": critical_floor_ok,
        "fit_quality_ok": fit_quality_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_electron_response()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "l'electron suit une loi de reponse continue kappa(n) extrapolable au-dela de n=4",
        "case_control": "kappa_2, kappa_3, kappa_4, extrapolation n=5,6,7",
        "observable": "kappa(n) = A n^{-p}",
        "expected": "suite monotone, pas de divergence, pas de saturation absurde",
        "measured": {
            "base_ns": result["base_ns"],
            "base_kappas": result["base_kappas"],
            "exponent": result["fit"]["exponent"],
            "amplitude": result["fit"]["amplitude"],
            "rmse": result["fit"]["rmse"],
            "relative_rmse": result["fit"]["relative_rmse"],
        },
        "extrapolated": result["extrapolated"],
        "monotone_ok": result["monotone_ok"],
        "positive_ok": result["positive_ok"],
        "saturation_absent_ok": result["saturation_absent_ok"],
        "critical_floor_ok": result["critical_floor_ok"],
        "fit_quality_ok": result["fit_quality_ok"],
        "verdict": result["verdict"],
        "reference": "V5-N and V6-e power-law response",
    }

    json_path = outdir / f"v7electronic_check_{timestamp}.json"
    txt_path = outdir / f"v7electronic_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V7 ELECTRIC check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"exponent: {result['fit']['exponent']:.15f}",
        f"amplitude: {result['fit']['amplitude']:.15f}",
        f"rmse: {result['fit']['rmse']:.15e}",
        f"relative_rmse: {result['fit']['relative_rmse']:.6f}",
        f"monotone_ok: {result['monotone_ok']}",
        f"positive_ok: {result['positive_ok']}",
        f"saturation_absent_ok: {result['saturation_absent_ok']}",
        f"critical_floor_ok: {result['critical_floor_ok']}",
        f"fit_quality_ok: {result['fit_quality_ok']}",
        "",
        "Sequence:",
    ]
    for n_value, kappa_value in zip(result["base_ns"], result["base_kappas"]):
        lines.append(f"- n={n_value:.0f} kappa={kappa_value:.15e}")
    for entry in result["extrapolated"]:
        lines.append(f"- n={entry['n']:.0f} kappa={entry['kappa']:.15e}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V7 multi-order electron response.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()