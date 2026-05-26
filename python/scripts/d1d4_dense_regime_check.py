"""Check the D1 / D4 balance in the dense regime.

The expected result is a clear density-driven crossover: D4 rises with
electron density, a balance point appears, and the low/high sides straddle
the D1 proxy as the model becomes degenerate.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from d1d4_model import close_enough, d1_proxy, density_for_balance, density_ratio_expected, fermi_balance_ev, fermi_pressure_pa


REFERENCE_CASE = {"symbol": "Pb", "name": "Lead-like dense reference", "ionization_ev": 7.4167, "principal_n": 6.0}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_point(d1_value: float, electron_density_m3: float, label: str) -> dict:
    d4_pressure = fermi_pressure_pa(electron_density_m3)
    d4_balance = fermi_balance_ev(electron_density_m3)
    return {
        "label": label,
        "electron_density_m3": electron_density_m3,
        "D1": d1_value,
        "D4_pressure_pa": d4_pressure,
        "D4_balance_ev": d4_balance,
        "balance_gap": abs(d1_value - d4_balance),
        "ok_low": d1_value > d4_balance,
        "ok_mid": close_enough(d1_value, d4_balance, rel_tol=1e-6, abs_tol=1e-6),
        "ok_high": d4_balance > d1_value,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "d1d4"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    d1_value = d1_proxy(REFERENCE_CASE["ionization_ev"], REFERENCE_CASE["principal_n"])
    balance_density = density_for_balance(d1_value)
    densities = [balance_density / 8.0, balance_density / 2.0, balance_density, balance_density * 2.0, balance_density * 8.0]
    labels = ["deep_dense_low", "dense_low", "balance", "dense_high", "deep_dense_high"]
    points = [evaluate_point(d1_value, density, label) for density, label in zip(densities, labels)]

    pressure_ratios = [points[index + 1]["D4_pressure_pa"] / points[index]["D4_pressure_pa"] for index in range(len(points) - 1)]
    expected_ratios = [density_ratio_expected(densities[index], densities[index + 1]) for index in range(len(densities) - 1)]

    scaling_ok = all(close_enough(actual, expected) for actual, expected in zip(pressure_ratios, expected_ratios))
    balance_ok = points[2]["ok_mid"] and points[2]["balance_gap"] < 1e-6
    regime_switch_ok = points[0]["ok_low"] and points[4]["ok_high"]
    continuity_ok = all(next_point["D4_balance_ev"] > current_point["D4_balance_ev"] for current_point, next_point in zip(points[:-1], points[1:]))
    verdict = "supported" if scaling_ok and balance_ok and regime_switch_ok and continuity_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "scaling_ok": scaling_ok,
        "balance_ok": balance_ok,
        "regime_switch_ok": regime_switch_ok,
        "continuity_ok": continuity_ok,
        "reference_case": {**REFERENCE_CASE, "D1": d1_value, "balance_density_m3": balance_density},
        "points": points,
        "pressure_ratios": pressure_ratios,
        "expected_pressure_ratios": expected_ratios,
        "regime": "dense",
        "hypothesis": "D4 grows with density, crosses D1 near the balance density, and remains continuous across the crossover",
        "case_control": "a lead-like dense reference probed below, at, and above the D1 = D4 balance density",
        "observable": "D1 versus D4_balance, the balance gap, and the pressure n_e^(5/3) scaling",
    }

    json_path = outdir / f"d1d4_dense_regime_check_{timestamp}.json"
    txt_path = outdir / f"d1d4_dense_regime_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "D1/D4 dense regime check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"scaling_ok: {scaling_ok}",
        f"balance_ok: {balance_ok}",
        f"regime_switch_ok: {regime_switch_ok}",
        f"continuity_ok: {continuity_ok}",
        "",
        f"Reference D1: {d1_value:.6f}",
        f"Balance density: {balance_density:.6e}",
        "",
        "Points:",
    ]
    for point in points:
        lines.append(
            f"- {point['label']}: n_e={point['electron_density_m3']:.6e} D1={point['D1']:.6f} D4_balance={point['D4_balance_ev']:.6f} gap={point['balance_gap']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the D1 / D4 balance in the dense regime.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()