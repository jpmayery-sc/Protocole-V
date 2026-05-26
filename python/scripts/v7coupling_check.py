"""Check the V7 coupling field alpha(E, n, r)."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from alphageometricport_check import evaluate_geometric_port
from alphatorsionorder_check import evaluate_torsion_order
from alphaenergyrunning_check import evaluate_running_coupling


E_GRID = [45.0, 50.0, 55.0]
N_GRID = [5.0, 6.0, 7.0]
R_GRID = [4.0, 5.0, 6.0]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_coupling_field() -> dict:
    energy_result = evaluate_running_coupling()
    torsion_result = evaluate_torsion_order()
    geometric_result = evaluate_geometric_port()

    alpha0 = geometric_result["alpha_ref"]
    aE = energy_result["dalphadE"]
    torsion_fit = evaluate_torsion_order()
    amplitude = 0.08043147830901778
    exponent = 4.9456681557600435
    ar = abs(geometric_result["delta_Dtheta_rad"])

    def kappa(n_value: float) -> float:
        return amplitude * (n_value ** (-exponent))

    def alpha_field(energy: float, n_value: float, radius: float) -> float:
        return alpha0 + aE * energy + kappa(n_value) + ar / radius

    grid = []
    values = []
    for energy in E_GRID:
        for n_value in N_GRID:
            for radius in R_GRID:
                value = alpha_field(energy, n_value, radius)
                grid.append(
                    {
                        "E": energy,
                        "n": n_value,
                        "r": radius,
                        "alpha": value,
                    }
                )
                values.append(value)

    domain_ok = all(0.0 < value < 1.0 for value in values)
    partial_E_positive_ok = alpha_field(55.0, 6.0, 5.0) > alpha_field(45.0, 6.0, 5.0)
    partial_n_negative_ok = alpha_field(50.0, 5.0, 5.0) > alpha_field(50.0, 7.0, 5.0)
    partial_r_negative_ok = alpha_field(50.0, 6.0, 4.0) > alpha_field(50.0, 6.0, 6.0)
    stability_range = max(values) - min(values)
    stability_surface_ok = stability_range < 1.0e-4
    stability_mean = sum(values) / len(values)
    stability_band_ok = stability_mean > min(values) and stability_mean < max(values)
    verdict = "conforme" if (
        domain_ok
        and partial_E_positive_ok
        and partial_n_negative_ok
        and partial_r_negative_ok
        and stability_surface_ok
        and stability_band_ok
    ) else "rejette"

    return {
        "alpha0": alpha0,
        "aE": aE,
        "amplitude": amplitude,
        "exponent": exponent,
        "ar": ar,
        "grid": grid,
        "values": values,
        "domain_ok": domain_ok,
        "partial_E_positive_ok": partial_E_positive_ok,
        "partial_n_negative_ok": partial_n_negative_ok,
        "partial_r_negative_ok": partial_r_negative_ok,
        "stability_range": stability_range,
        "stability_surface_ok": stability_surface_ok,
        "stability_band_ok": stability_band_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_coupling_field()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "alpha est un champ dynamique dependant de l'energie, de l'ordre n et de la geometriE D2",
        "case_control": "alpha(E,n,r) = alpha0 + aE E + a_n n^-p + a_r/r",
        "observable": "surface alpha(E,n,r)",
        "expected": "domaine physique, derivees coherentes, surface de stabilite locale",
        "measured": {
            "alpha0": result["alpha0"],
            "aE": result["aE"],
            "amplitude": result["amplitude"],
            "exponent": result["exponent"],
            "ar": result["ar"],
            "domain_ok": result["domain_ok"],
            "partial_E_positive_ok": result["partial_E_positive_ok"],
            "partial_n_negative_ok": result["partial_n_negative_ok"],
            "partial_r_negative_ok": result["partial_r_negative_ok"],
            "stability_range": result["stability_range"],
            "stability_surface_ok": result["stability_surface_ok"],
            "stability_band_ok": result["stability_band_ok"],
        },
        "grid": result["grid"],
        "verdict": result["verdict"],
        "reference": "V5-E + V5-N + V6-D2",
    }

    json_path = outdir / f"v7coupling_check_{timestamp}.json"
    txt_path = outdir / f"v7coupling_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V7 coupling check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"alpha0: {result['alpha0']:.15f}",
        f"aE: {result['aE']:.15e}",
        f"amplitude: {result['amplitude']:.15f}",
        f"exponent: {result['exponent']:.15f}",
        f"ar: {result['ar']:.15e}",
        f"domain_ok: {result['domain_ok']}",
        f"partial_E_positive_ok: {result['partial_E_positive_ok']}",
        f"partial_n_negative_ok: {result['partial_n_negative_ok']}",
        f"partial_r_negative_ok: {result['partial_r_negative_ok']}",
        f"stability_range: {result['stability_range']:.6e}",
        f"stability_surface_ok: {result['stability_surface_ok']}",
        f"stability_band_ok: {result['stability_band_ok']}",
        "",
        "Grid sample:",
    ]
    for entry in result["grid"][:9]:
        lines.append(f"- E={entry['E']:.1f} n={entry['n']:.0f} r={entry['r']:.1f} alpha={entry['alpha']:.15f}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V7 dynamic coupling field alpha(E,n,r).")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()