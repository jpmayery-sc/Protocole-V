"""Check the V6-electron channel from alpha port."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from alphatorsionorder_check import evaluate_torsion_order


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
    return {
        "slope": slope,
        "intercept": intercept,
        "exponent": exponent,
        "predicted": predicted,
        "rmse": rmse,
        "relative_rmse": relative_rmse,
    }


def evaluate_electron_channel() -> dict:
    torsion = evaluate_torsion_order()
    cases = torsion["cases"]
    ns = [float(case["n"]) for case in cases]
    kappas = [float(case["kappa_n"]) for case in cases]
    fit = fit_power_law(ns, kappas)

    decreasing_ok = all(later < earlier for earlier, later in zip(kappas, kappas[1:]))
    exponent_ok = fit["exponent"] > 1.0
    fit_quality_ok = fit["relative_rmse"] < 0.15
    channel_ok = decreasing_ok and exponent_ok and fit_quality_ok and torsion["verdict"] == "conforme"
    verdict = "conforme" if channel_ok else "rejette"

    return {
        "n_values": ns,
        "kappas": kappas,
        "fit": fit,
        "decreasing_ok": decreasing_ok,
        "exponent_ok": exponent_ok,
        "fit_quality_ok": fit_quality_ok,
        "channel_ok": channel_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_electron_channel()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "l'electron est un canal D1-D2-D3 dont la reponse effective se lit dans les pentes V5-N",
        "case_control": "kappa_2, kappa_3, kappa_4",
        "observable": "ajustement loi puissance kappa_n ~ n^{-p}",
        "expected": "decroissance monotone avec une loi simple et un residu faible",
        "measured": {
            "n_values": result["n_values"],
            "kappas": result["kappas"],
            "exponent": result["fit"]["exponent"],
            "slope": result["fit"]["slope"],
            "rmse": result["fit"]["rmse"],
            "relative_rmse": result["fit"]["relative_rmse"],
        },
        "decreasing_ok": result["decreasing_ok"],
        "exponent_ok": result["exponent_ok"],
        "fit_quality_ok": result["fit_quality_ok"],
        "channel_ok": result["channel_ok"],
        "verdict": result["verdict"],
        "reference": "V5-N torsion-response power law",
    }

    json_path = outdir / f"electronchannelfromalphacheck_{timestamp}.json"
    txt_path = outdir / f"electronchannelfromalphacheck_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Electron channel from alpha check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"exponent: {result['fit']['exponent']:.15f}",
        f"slope: {result['fit']['slope']:.15f}",
        f"rmse: {result['fit']['rmse']:.15e}",
        f"relative_rmse: {result['fit']['relative_rmse']:.6f}",
        f"decreasing_ok: {result['decreasing_ok']}",
        f"exponent_ok: {result['exponent_ok']}",
        f"fit_quality_ok: {result['fit_quality_ok']}",
        f"channel_ok: {result['channel_ok']}",
        "",
        "Cases:",
    ]
    for n_value, kappa_value in zip(result["n_values"], result["kappas"]):
        lines.append(f"- n={n_value:.0f} kappa={kappa_value:.15e}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V6 electron channel from alpha.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
