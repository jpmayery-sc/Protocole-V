"""Check the dense branch of the regime-physics grid."""
from __future__ import annotations

import argparse
import json
import time

from d1d4_model import close_enough, density_for_balance, density_ratio_expected, d1_proxy
from regime_physics_common import write_report
from run_regime_physics import run_regime


REFERENCE_CASE = {"symbol": "Pb", "ionization_ev": 7.4167, "principal_n": 6.0}


def run_check(output_dir: str | None = None) -> dict:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    d1_value = d1_proxy(REFERENCE_CASE["ionization_ev"], REFERENCE_CASE["principal_n"])
    balance_density = density_for_balance(d1_value)
    densities = [balance_density / 16.0, balance_density / 8.0, balance_density / 2.0, balance_density, balance_density * 2.0, balance_density * 8.0, balance_density * 16.0]
    labels = ["ultra_dense_low", "deep_dense_low", "dense_low", "balance", "dense_high", "deep_dense_high", "ultra_dense_high"]
    points = []
    for density, label in zip(densities, labels):
        launcher = run_regime(
            "dense",
            element=REFERENCE_CASE["symbol"],
            ionization_ev=REFERENCE_CASE["ionization_ev"],
            principal_n=REFERENCE_CASE["principal_n"],
            electron_density_m3=density,
        )
        points.append(
            {
                "label": label,
                "electron_density_m3": density,
                "D1_proxy": launcher.get("D1_proxy", d1_value),
                "D4_pressure_pa": launcher["D4_pressure_pa"],
                "D4_balance_ev": launcher["D4_balance_ev"],
                "balance_gap": abs(launcher.get("D1_proxy", d1_value) - launcher["D4_balance_ev"]),
                "launcher_grid": launcher["dominant_grid"],
                "ok_low": launcher.get("D1_proxy", d1_value) > launcher["D4_balance_ev"],
                "ok_mid": close_enough(launcher.get("D1_proxy", d1_value), launcher["D4_balance_ev"], rel_tol=1e-6, abs_tol=1e-6),
                "ok_high": launcher["D4_balance_ev"] > launcher.get("D1_proxy", d1_value),
            }
        )

    pressure_ratios = [points[index + 1]["D4_pressure_pa"] / points[index]["D4_pressure_pa"] for index in range(len(points) - 1)]
    expected_ratios = [density_ratio_expected(densities[index], densities[index + 1]) for index in range(len(densities) - 1)]
    scaling_ok = all(close_enough(actual, expected) for actual, expected in zip(pressure_ratios, expected_ratios))
    launcher_ok = all(point["launcher_grid"] == "D1 + D4" for point in points)
    balance_ok = points[3]["ok_mid"] and points[3]["balance_gap"] < 1.0e-12
    regime_switch_ok = points[0]["ok_low"] and points[-1]["ok_high"]
    continuity_ok = all(next_point["D4_balance_ev"] > current_point["D4_balance_ev"] for current_point, next_point in zip(points[:-1], points[1:]))
    verdict = "supported" if scaling_ok and launcher_ok and balance_ok and regime_switch_ok and continuity_ok else "contradicted"

    payload = {
        "timestamp": timestamp,
        "suite": "regime_physics",
        "regime": "dense",
        "verdict": verdict,
        "hypothesis": "Dense matter admits a local D1 ~= D4 balance that moves continuously with density",
        "case_control": "Pb-like dense reference probed below, at, and above the balance density",
        "observable": "D1_proxy versus D4_balance and the density-driven crossover",
        "checks": ["D1 and D4 cross locally", "pressure scales as n_e^(5/3)", "launcher routes dense cases to D1 + D4"],
        "launcher_ok": launcher_ok,
        "scaling_ok": scaling_ok,
        "balance_ok": balance_ok,
        "regime_switch_ok": regime_switch_ok,
        "continuity_ok": continuity_ok,
        "reference_case": {**REFERENCE_CASE, "D1_proxy": d1_value, "balance_density_m3": balance_density},
        "cases": points,
        "pressure_ratios": pressure_ratios,
        "expected_pressure_ratios": expected_ratios,
    }
    json_path, txt_path = write_report("Regime dense check", "regime_dense_check", payload, output_dir)
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the dense branch of the regime-physics grid.")
    parser.add_argument("--output-dir", default=None, help="Directory for the regime report")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()