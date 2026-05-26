"""Recalculate Zeff* for the tetrel series C -> Pb.

This script evaluates the user-provided correction:

    Zeff_star = Zeff + a*k + b*L + c*Z^2 + d*H

For the tetrel family, H = 0 and k = 0 throughout, so the correction reduces
to the L term plus the relativistic Z^2 term.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6
A_K = 0.0
B_L = 0.25
C_Z2 = 1.1e-4
D_H = 0.0

FAMILY = [
    {"symbol": "C", "Z": 6, "period": 2, "mass_u": 12.011, "radius_pm": 67.0, "ionization_ev": 11.2603, "k": 0.0, "L": 0.0, "H": 0.0},
    {"symbol": "Si", "Z": 14, "period": 3, "mass_u": 28.085, "radius_pm": 111.0, "ionization_ev": 8.1517, "k": 0.0, "L": 1.0, "H": 0.0},
    {"symbol": "Ge", "Z": 32, "period": 4, "mass_u": 72.630, "radius_pm": 125.0, "ionization_ev": 7.8994, "k": 0.0, "L": 2.0, "H": 0.0},
    {"symbol": "Sn", "Z": 50, "period": 5, "mass_u": 118.710, "radius_pm": 145.0, "ionization_ev": 7.3439, "k": 0.0, "L": 3.0, "H": 0.0},
    {"symbol": "Pb", "Z": 82, "period": 6, "mass_u": 207.200, "radius_pm": 154.0, "ionization_ev": 7.4167, "k": 0.0, "L": 3.0, "H": 0.0},
]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def trend(values: list[float]) -> str:
    if all(b > a for a, b in zip(values[:-1], values[1:])):
        return "increasing"
    if all(b < a for a, b in zip(values[:-1], values[1:])):
        return "decreasing"
    return "mixed"


def rmse(y_true: list[float], y_pred: list[float]) -> float:
    return math.sqrt(sum((true - pred) ** 2 for true, pred in zip(y_true, y_pred)) / len(y_true))


def run_check(output_dir: str | Path | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    series = []
    zeff_values = []
    zeff_star_values = []
    radii = []
    ionizations = []

    for item in FAMILY:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        zeff_star = zeff + (A_K * item["k"]) + (B_L * item["L"]) + (C_Z2 * (item["Z"] ** 2)) + (D_H * item["H"])
        series.append(
            {
                **item,
                "zeff_proxy": round(zeff, 6),
                "zeff_star": round(zeff_star, 6),
            }
        )
        zeff_values.append(zeff)
        zeff_star_values.append(zeff_star)
        radii.append(item["radius_pm"])
        ionizations.append(item["ionization_ev"])

    verdict = "supported" if trend(zeff_star_values) == "increasing" else "contradicted"
    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "hypothesis": "the user-provided Zeff* correction makes the tetrel family C -> Pb monotone",
        "case_control": "standard Zeff proxy versus corrected Zeff* on the tetrel family",
        "observable": "monotonicity of Zeff* and comparison with the raw radius and ionization trends",
        "expected": "Zeff* becomes increasing across C -> Pb",
        "measured": {
            "radius_trend": trend(radii),
            "ionization_trend": trend(ionizations),
            "zeff_trend": trend(zeff_values),
            "zeff_star_trend": trend(zeff_star_values),
            "zeff_values": [round(value, 6) for value in zeff_values],
            "zeff_star_values": [round(value, 6) for value in zeff_star_values],
            "series": series,
        },
        "reference": {
            "a_k": A_K,
            "b_L": B_L,
            "c_z2": C_Z2,
            "d_H": D_H,
        },
    }

    json_path = outdir / f"tetrel_zeff_star_check_{timestamp}.json"
    txt_path = outdir / f"tetrel_zeff_star_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Tetrel Zeff* check\n")
        handle.write(f"Timestamp: {timestamp}\n")
        handle.write(f"Hypothese: {data['hypothesis']}\n")
        handle.write(f"Cas de controle: {data['case_control']}\n")
        handle.write(f"Observable: {data['observable']}\n")
        handle.write(f"Attendu: {data['expected']}\n")
        handle.write(f"Mesuree: {data['measured']['zeff_star_trend']}\n")
        handle.write(f"Verdict: {verdict}\n")
        handle.write("Critere de rejet: Zeff* non monotone sur C -> Pb\n")
        handle.write(f"Reference: a={A_K}, b={B_L}, c={C_Z2}, d={D_H}\n")
        handle.write(f"JSON: {json_path}\n")
        handle.write(f"TXT: {txt_path}\n")

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