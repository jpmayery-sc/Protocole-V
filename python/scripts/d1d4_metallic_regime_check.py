"""Check the D1 / D4 balance in the metallic regime.

The expected result is that D4 is no longer negligible, but D1 still dominates
and the Fermi scale sits in the few-eV window characteristic of metals.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from d1d4_model import close_enough, d1_proxy, density_ratio_expected, fermi_balance_ev, fermi_pressure_pa


CASES = [
    {"symbol": "Al", "name": "Aluminum-like metal", "ionization_ev": 5.9858, "principal_n": 3.0, "electron_density_m3": 3.0e28},
    {"symbol": "Fe", "name": "Iron-like metal", "ionization_ev": 7.9024, "principal_n": 4.0, "electron_density_m3": 5.0e28},
    {"symbol": "Cu", "name": "Copper-like metal", "ionization_ev": 7.7264, "principal_n": 4.0, "electron_density_m3": 7.0e28},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    d1_value = d1_proxy(case["ionization_ev"], case["principal_n"])
    d4_pressure = fermi_pressure_pa(case["electron_density_m3"])
    d4_balance = fermi_balance_ev(case["electron_density_m3"])
    return {
        **case,
        "D1": d1_value,
        "D4_pressure_pa": d4_pressure,
        "D4_balance_ev": d4_balance,
        "D4_over_D1": d4_balance / d1_value,
        "domination_ok": d1_value > d4_balance,
        "window_ok": 2.0 <= d4_balance <= 4.5,
        "ok": d1_value > d4_balance,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "d1d4"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    cases = [evaluate_case(case) for case in CASES]
    pressure_ratios = [cases[index + 1]["D4_pressure_pa"] / cases[index]["D4_pressure_pa"] for index in range(len(cases) - 1)]
    expected_ratios = [density_ratio_expected(cases[index]["electron_density_m3"], cases[index + 1]["electron_density_m3"]) for index in range(len(cases) - 1)]

    pressure_scaling_ok = all(close_enough(actual, expected) for actual, expected in zip(pressure_ratios, expected_ratios))
    d1_dominates_ok = all(case["D1"] > case["D4_balance_ev"] for case in cases)
    fermi_window_ok = any(2.0 <= case["D4_balance_ev"] <= 4.5 for case in cases)
    nonzero_ok = all(case["D4_balance_ev"] > 0.0 for case in cases)
    verdict = "supported" if pressure_scaling_ok and d1_dominates_ok and fermi_window_ok and nonzero_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "pressure_scaling_ok": pressure_scaling_ok,
        "d1_dominates_ok": d1_dominates_ok,
        "fermi_window_ok": fermi_window_ok,
        "nonzero_ok": nonzero_ok,
        "cases": cases,
        "pressure_ratios": pressure_ratios,
        "expected_pressure_ratios": expected_ratios,
        "regime": "metallic",
        "hypothesis": "D4 is small but nonzero in metals and stays below D1 in the reference metallic window",
        "case_control": "aluminum-like, iron-like, and copper-like density windows",
        "observable": "D1 versus D4_balance, plus the few-eV Fermi window and pressure scaling",
    }

    json_path = outdir / f"d1d4_metallic_regime_check_{timestamp}.json"
    txt_path = outdir / f"d1d4_metallic_regime_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "D1/D4 metallic regime check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"pressure_scaling_ok: {pressure_scaling_ok}",
        f"d1_dominates_ok: {d1_dominates_ok}",
        f"fermi_window_ok: {fermi_window_ok}",
        f"nonzero_ok: {nonzero_ok}",
        "",
        "Cases:",
    ]
    for case in cases:
        lines.append(
            f"- {case['symbol']}: n_e={case['electron_density_m3']:.3e} D1={case['D1']:.6f} D4_balance={case['D4_balance_ev']:.6f} D4_pressure={case['D4_pressure_pa']:.6e} domination_ok={case['domination_ok']} window_ok={case['window_ok']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the D1 / D4 balance in the metallic regime.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
