"""Check the atomic branch of the regime-physics grid."""
from __future__ import annotations

import argparse
import json
import time

from d1d4_model import close_enough, d1_proxy, density_ratio_expected, fermi_balance_ev, fermi_pressure_pa
from regime_physics_common import write_report
from run_regime_physics import run_regime


CASES = [
    {"symbol": "Li", "ionization_ev": 5.3917, "principal_n": 2.0, "electron_density_m3": 2.0e20},
    {"symbol": "H", "ionization_ev": 13.6, "principal_n": 1.0, "electron_density_m3": 1.0e20},
    {"symbol": "He", "ionization_ev": 24.587, "principal_n": 1.0, "electron_density_m3": 5.0e20},
    {"symbol": "Ne", "ionization_ev": 21.564, "principal_n": 2.0, "electron_density_m3": 1.0e21},
]


def run_check(output_dir: str | None = None) -> dict:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    cases = []
    for case in CASES:
        launcher = run_regime(
            "atomique",
            element=case["symbol"],
            ionization_ev=case["ionization_ev"],
            principal_n=case["principal_n"],
            electron_density_m3=case["electron_density_m3"],
        )
        d1_value = d1_proxy(case["ionization_ev"], case["principal_n"])
        d4_pressure = fermi_pressure_pa(case["electron_density_m3"])
        d4_balance = fermi_balance_ev(case["electron_density_m3"])
        cases.append(
            {
                **case,
                "launcher_grid": launcher["dominant_grid"],
                "D1_proxy": d1_value,
                "D4_pressure_pa": d4_pressure,
                "D4_balance_ev": d4_balance,
                "D4_over_D1": d4_balance / d1_value,
                "verdict": "supported" if d1_value > d4_balance and d4_balance / d1_value < 5.0e-4 else "contradicted",
            }
        )

    pressure_ratios = [cases[index + 1]["D4_pressure_pa"] / cases[index]["D4_pressure_pa"] for index in range(len(cases) - 1)]
    expected_ratios = [density_ratio_expected(cases[index]["electron_density_m3"], cases[index + 1]["electron_density_m3"]) for index in range(len(cases) - 1)]
    pressure_scaling_ok = all(close_enough(actual, expected) for actual, expected in zip(pressure_ratios, expected_ratios))
    launcher_ok = all(case["launcher_grid"] == "D1" for case in cases)
    d1_dominates_ok = all(case["D1_proxy"] > case["D4_balance_ev"] for case in cases)
    negligible_ok = max(case["D4_over_D1"] for case in cases) < 5.0e-4
    verdict = "supported" if pressure_scaling_ok and launcher_ok and d1_dominates_ok and negligible_ok else "contradicted"

    payload = {
        "timestamp": timestamp,
        "suite": "regime_physics",
        "regime": "atomique",
        "verdict": verdict,
        "hypothesis": "D1 dominates in the atomic regime while D4 stays negligible",
        "case_control": "H, He, and Ne atomic ladder with low electron density",
        "observable": "D1_proxy versus D4_balance and the n_e^(5/3) pressure scaling",
        "checks": ["D1 dominates", "D4 remains negligible", "raw pressure follows n_e^(5/3)", "launcher routes the atomic branch to D1"],
        "pressure_scaling_ok": pressure_scaling_ok,
        "launcher_ok": launcher_ok,
        "d1_dominates_ok": d1_dominates_ok,
        "negligible_ok": negligible_ok,
        "cases": cases,
        "pressure_ratios": pressure_ratios,
        "expected_pressure_ratios": expected_ratios,
    }
    json_path, txt_path = write_report("Regime atomique check", "regime_atomique_check", payload, output_dir)
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the atomic branch of the regime-physics grid.")
    parser.add_argument("--output-dir", default=None, help="Directory for the regime report")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()