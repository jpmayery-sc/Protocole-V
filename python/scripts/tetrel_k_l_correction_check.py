"""Test the candidate k/L correction on the tetrel family.

The goal is to turn the structural correction hypothesis into a concrete,
falsifiable check:

    Z_eff_star = Z_eff + a * k + b * L

For the tetrel family, k is kept at 0 and L encodes the local bonding regime.
We compare a baseline fit of radius against Z_eff with an augmented fit against
Z_eff_star, and check whether the augmented model reduces residuals.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6
FAMILY = [
    {"symbol": "C", "name": "Carbon", "period": 2, "mass_u": 12.011, "radius_pm": 67.0, "ionization_ev": 11.2603, "k": 0.0, "L": 0.0},
    {"symbol": "Si", "name": "Silicon", "period": 3, "mass_u": 28.085, "radius_pm": 111.0, "ionization_ev": 8.1517, "k": 0.0, "L": 1.0},
    {"symbol": "Ge", "name": "Germanium", "period": 4, "mass_u": 72.630, "radius_pm": 125.0, "ionization_ev": 7.8994, "k": 0.0, "L": 2.0},
    {"symbol": "Sn", "name": "Tin", "period": 5, "mass_u": 118.710, "radius_pm": 145.0, "ionization_ev": 7.3439, "k": 0.0, "L": 3.0},
    {"symbol": "Pb", "name": "Lead", "period": 6, "mass_u": 207.200, "radius_pm": 154.0, "ionization_ev": 7.4167, "k": 0.0, "L": 3.0},
]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def linear_fit(xs: list[float], ys: list[float]) -> tuple[float, float]:
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = numerator / denominator if denominator else 0.0
    intercept = mean_y - slope * mean_x
    return slope, intercept


def rmse(y_true: list[float], y_pred: list[float]) -> float:
    return math.sqrt(sum((true - pred) ** 2 for true, pred in zip(y_true, y_pred)) / len(y_true))


def build_observables(series: list[dict]) -> dict:
    items = []
    zeff_values = []
    corrected_values = []
    radii = []
    masses = []
    ks = []
    ls = []

    for item in series:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        items.append({**item, "zeff_proxy": round(zeff, 6)})
        zeff_values.append(zeff)
        radii.append(item["radius_pm"])
        masses.append(item["mass_u"])
        ks.append(item["k"])
        ls.append(item["L"])

    return {
        "series": items,
        "zeff_values": zeff_values,
        "radii": radii,
        "masses": masses,
        "ks": ks,
        "ls": ls,
    }


def fit_baseline(observables: dict) -> dict:
    zeff_fit = linear_fit(observables["zeff_values"], observables["radii"])
    baseline_pred = [zeff_fit[0] * value + zeff_fit[1] for value in observables["zeff_values"]]
    return {
        "fit": {"slope": zeff_fit[0], "intercept": zeff_fit[1]},
        "predicted": baseline_pred,
        "rmse": rmse(observables["radii"], baseline_pred),
    }


def fit_augmented(observables: dict) -> dict:
    augmented_axis = [zeff + 1.5 * k + 0.9 * l for zeff, k, l in zip(observables["zeff_values"], observables["ks"], observables["ls"])]
    fit = linear_fit(augmented_axis, observables["radii"])
    predicted = [fit[0] * value + fit[1] for value in augmented_axis]
    return {
        "fit": {"slope": fit[0], "intercept": fit[1]},
        "predicted": predicted,
        "rmse": rmse(observables["radii"], predicted),
        "augmented_axis": augmented_axis,
    }


def trend(values: list[float]) -> str:
    if all(b > a for a, b in zip(values[:-1], values[1:])):
        return "increasing"
    if all(b < a for a, b in zip(values[:-1], values[1:])):
        return "decreasing"
    return "mixed"


def run_check(output_dir: str | Path | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    observables = build_observables(FAMILY)
    baseline = fit_baseline(observables)
    augmented = fit_augmented(observables)

    augmented_better = augmented["rmse"] < baseline["rmse"]
    monotone_radius = trend(observables["radii"]) == "increasing"
    monotone_zeff = trend(observables["zeff_values"]) == "increasing"
    monotone_augmented = trend(augmented["augmented_axis"]) == "increasing"

    verdict = "supported" if augmented_better and monotone_radius and monotone_zeff and monotone_augmented else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "augmented_better": augmented_better,
        "monotone_radius": monotone_radius,
        "monotone_zeff": monotone_zeff,
        "monotone_augmented": monotone_augmented,
        "baseline": baseline,
        "augmented": augmented,
        "hypothesis": "for the tetrel family, adding the local L regime to Z_eff reduces radius residuals",
        "case_control": "baseline Z_eff fit versus augmented Z_eff_star = Z_eff + a*k + b*L",
        "observable": "radius residuals on the tetrel family",
        "family": observables["series"],
    }

    json_path = outdir / f"tetrel_k_l_correction_check_{timestamp}.json"
    txt_path = outdir / f"tetrel_k_l_correction_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Tetrel k/L correction check\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write(f"Hypothese: {data['hypothesis']}\n")
        handle.write(f"Cas de controle: {data['case_control']}\n")
        handle.write(f"Observable: {data['observable']}\n")
        handle.write(f"Verdict: {verdict}\n\n")
        handle.write("Famille:\n")
        for item in observables["series"]:
            handle.write(
                f"- {item['symbol']}: radius={item['radius_pm']:.1f} pm, ie={item['ionization_ev']:.4f} eV, "
                f"zeff={item['zeff_proxy']}, k={item['k']}, L={item['L']}\n"
            )
        handle.write("\nBaseline:\n")
        handle.write(f"- fit_slope: {baseline['fit']['slope']:.6f}\n")
        handle.write(f"- fit_intercept: {baseline['fit']['intercept']:.6f}\n")
        handle.write(f"- rmse: {baseline['rmse']:.6f}\n")
        handle.write("\nAugmented:\n")
        handle.write(f"- fit_slope: {augmented['fit']['slope']:.6f}\n")
        handle.write(f"- fit_intercept: {augmented['fit']['intercept']:.6f}\n")
        handle.write(f"- rmse: {augmented['rmse']:.6f}\n")
        handle.write(f"- augmented_better: {augmented_better}\n")
        handle.write(f"- monotone_augmented: {monotone_augmented}\n")

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