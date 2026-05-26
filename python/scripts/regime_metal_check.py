"""Check the metallic branch of the regime-physics grid."""
from __future__ import annotations

import argparse
import json
import time

from d1d4_model import close_enough, d1_proxy, density_ratio_expected, fermi_balance_ev, fermi_pressure_pa
from regime_physics_common import write_report
from run_regime_physics import run_regime


CASES = [
    {"symbol": "Mg", "ionization_ev": 7.6462, "principal_n": 3.0, "electron_density_m3": 1.8e28},
    {"symbol": "Na", "ionization_ev": 5.1391, "principal_n": 3.0, "electron_density_m3": 2.5e28},
    {"symbol": "Al", "ionization_ev": 5.9858, "principal_n": 3.0, "electron_density_m3": 3.0e28},
    {"symbol": "Cu", "ionization_ev": 7.7264, "principal_n": 4.0, "electron_density_m3": 7.0e28},
    {"symbol": "Ag", "ionization_ev": 7.5762, "principal_n": 5.0, "electron_density_m3": 5.5e28},
]


def run_check(output_dir: str | None = None) -> dict:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    cases = []
    for case in CASES:
        launcher = run_regime(
            "metal",
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
                "window_ok": 1.1 <= d4_balance <= 2.8,
                "verdict": "supported" if d1_value > d4_balance else "contradicted",
            }
        )

    pressure_ratios = [cases[index + 1]["D4_pressure_pa"] / cases[index]["D4_pressure_pa"] for index in range(len(cases) - 1)]
    expected_ratios = [density_ratio_expected(cases[index]["electron_density_m3"], cases[index + 1]["electron_density_m3"]) for index in range(len(cases) - 1)]
    pressure_scaling_ok = all(close_enough(actual, expected) for actual, expected in zip(pressure_ratios, expected_ratios))
    launcher_ok = all(case["launcher_grid"] == "D1 + D2 + D4" for case in cases)
    d1_dominates_ok = all(case["D1_proxy"] > case["D4_balance_ev"] for case in cases)
    window_ok = sum(1 for case in cases if case["window_ok"]) >= 3
    nonzero_ok = all(case["D4_balance_ev"] > 0.0 for case in cases)
    verdict = "supported" if pressure_scaling_ok and launcher_ok and d1_dominates_ok and window_ok and nonzero_ok else "contradicted"

    payload = {
        "timestamp": timestamp,
        "suite": "regime_physics",
        "regime": "metal",
        "verdict": verdict,
        "hypothesis": "Metals keep D4 moderate, below D1, while the Fermi scale stays in the few-eV window",
        "case_control": "Na, Al, and Cu density windows",
        "observable": "D1_proxy versus D4_balance and the few-eV Fermi window",
        "checks": ["D4 is moderate", "D1 still dominates", "launcher routes the metallic branch to D1 + D2 + D4"],
        "pressure_scaling_ok": pressure_scaling_ok,
        "launcher_ok": launcher_ok,
        "d1_dominates_ok": d1_dominates_ok,
        "window_ok": window_ok,
        "nonzero_ok": nonzero_ok,
        "cases": cases,
        "pressure_ratios": pressure_ratios,
        "expected_pressure_ratios": expected_ratios,
    }
    json_path, txt_path = write_report("Regime metal check", "regime_metal_check", payload, output_dir)
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the metallic branch of the regime-physics grid.")
    parser.add_argument("--output-dir", default=None, help="Directory for the regime report")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()