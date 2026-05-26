"""Recalculate Zeff* for the halogen series F -> At.

This transfer check uses the same correction tested on tetrels:

    Zeff_star = Zeff + a*k + b*L + c*Z^2 + d*H

For halogens, k = 0 and H = 0 throughout, so the correction reduces to the
L term plus the relativistic Z^2 term.
"""
from __future__ import annotations

import json
import math
import time
from pathlib import Path


R_H_EV = 13.6
A_K = 0.0
B_L = 0.25
C_Z2 = 1.1e-4
D_H = 0.0

FAMILY = [
    {"symbol": "F", "Z": 9, "period": 2, "mass_u": 18.998403163, "radius_pm": 64.0, "ionization_ev": 17.4228, "k": 0.0, "L": 0.0, "H": 0.0},
    {"symbol": "Cl", "Z": 17, "period": 3, "mass_u": 35.45, "radius_pm": 99.0, "ionization_ev": 12.9676, "k": 0.0, "L": 1.0, "H": 0.0},
    {"symbol": "Br", "Z": 35, "period": 4, "mass_u": 79.904, "radius_pm": 114.0, "ionization_ev": 11.8138, "k": 0.0, "L": 2.0, "H": 0.0},
    {"symbol": "I", "Z": 53, "period": 5, "mass_u": 126.90447, "radius_pm": 133.0, "ionization_ev": 10.4513, "k": 0.0, "L": 3.0, "H": 0.0},
    {"symbol": "At", "Z": 85, "period": 6, "mass_u": 210.0, "radius_pm": 150.0, "ionization_ev": 9.5, "k": 0.0, "L": 3.0, "H": 0.0},
]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def monotonicity(values: list[float]) -> str:
    increasing = all(b > a for a, b in zip(values[:-1], values[1:]))
    decreasing = all(b < a for a, b in zip(values[:-1], values[1:]))
    if increasing:
        return "increasing"
    if decreasing:
        return "decreasing"
    return "mixed"


def run_check(output_dir: str | Path | None = None) -> dict:
    root = Path(__file__).resolve().parents[1]
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
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

    measured = {
        "radius_trend": monotonicity(radii),
        "ionization_trend": monotonicity(ionizations),
        "zeff_trend": monotonicity(zeff_values),
        "zeff_star_trend": monotonicity(zeff_star_values),
        "zeff_values": [round(value, 6) for value in zeff_values],
        "zeff_star_values": [round(value, 6) for value in zeff_star_values],
        "series": series,
    }

    verdict = "supported" if measured["zeff_star_trend"] == "increasing" else "contradicted"
    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "hypothesis": "the user-provided Zeff* correction keeps the halogen family F -> At monotone",
        "case_control": "standard Zeff proxy versus corrected Zeff* on the halogen family",
        "observable": "monotonicity of Zeff* and comparison with the raw radius and ionization trends",
        "expected": "Zeff* becomes increasing across F -> At",
        "measured": measured,
        "reference": {
            "a_k": A_K,
            "b_L": B_L,
            "c_z2": C_Z2,
            "d_H": D_H,
        },
    }

    json_path = outdir / f"halogen_zeff_star_check_{timestamp}.json"
    txt_path = outdir / f"halogen_zeff_star_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Halogen Zeff* check\n")
        handle.write(f"Timestamp: {timestamp}\n")
        handle.write(f"Hypothese: {data['hypothesis']}\n")
        handle.write(f"Cas de controle: {data['case_control']}\n")
        handle.write(f"Observable: {data['observable']}\n")
        handle.write(f"Attendu: {data['expected']}\n")
        handle.write(f"Mesuree: {measured['zeff_star_trend']}\n")
        handle.write(f"Verdict: {verdict}\n")
        handle.write("Critere de rejet: Zeff* non monotone sur F -> At\n")
        handle.write(f"Reference: a={A_K}, b={B_L}, c={C_Z2}, d={D_H}\n")
        handle.write(f"JSON: {json_path}\n")
        handle.write(f"TXT: {txt_path}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {verdict}")


if __name__ == "__main__":
    run_check()