"""Check the D1 / D2 / D3 / D4 flow plan across representative regimes."""
from __future__ import annotations

import argparse
import json
import time

from d1d2_pipeline import d2 as d2_proxy
from d1d4_model import close_enough, d1_proxy, density_for_balance, density_ratio_expected, fermi_balance_ev, fermi_pressure_pa
from regime_physics_common import write_report
from run_regime_physics import run_regime


CASES = [
    {
        "label": "A",
        "regime": "atomique",
        "element": "Na",
        "ionization_ev": 5.1391,
        "principal_n": 3.0,
        "radius_pm": 186.0,
        "electron_density_m3": 2.0e20,
        "expected_grid": "D1",
        "structural_weight": 0.0,
    },
    {
        "label": "B",
        "regime": "metal",
        "element": "Al",
        "ionization_ev": 5.9858,
        "principal_n": 3.0,
        "radius_pm": 143.0,
        "electron_density_m3": 3.0e28,
        "expected_grid": "D1 + D2 + D4",
        "structural_weight": 0.0,
    },
    {
        "label": "C",
        "regime": "lanthanide",
        "element": "Ce",
        "ionization_ev": 5.5387,
        "principal_n": 6.0,
        "radius_pm": 185.0,
        "electron_density_m3": 4.5e28,
        "expected_grid": "D1 + D3",
        "structural_weight": 0.75,
    },
    {
        "label": "D",
        "regime": "dense",
        "element": "Pb",
        "ionization_ev": 7.4167,
        "principal_n": 6.0,
        "radius_pm": 154.0,
        "electron_density_m3": None,
        "dense_multiplier": 512.0,
        "expected_grid": "D1 + D4",
        "structural_weight": 0.0,
    },
]


def evaluate_case(case: dict) -> dict:
    d1_value = d1_proxy(case["ionization_ev"], case["principal_n"])
    d2_value = d2_proxy(case["ionization_ev"], case["radius_pm"])
    density = case["electron_density_m3"]
    if case["regime"] == "dense":
        density = density_for_balance(d1_value) * float(case.get("dense_multiplier", 1.0))
    assert density is not None

    d3_value = max(d1_value, d2_value) * float(case.get("structural_weight", 0.0))
    d4_pressure = fermi_pressure_pa(density)
    d4_balance = fermi_balance_ev(density)
    launcher = run_regime(
        case["regime"],
        element=case["element"],
        ionization_ev=case["ionization_ev"],
        principal_n=case["principal_n"],
        electron_density_m3=density,
    )

    flow_total = d1_value + d2_value + d3_value + d4_balance
    return {
        **case,
        "electron_density_m3": density,
        "reference_density_m3": density_for_balance(d1_value),
        "launcher_grid": launcher["dominant_grid"],
        "D1_proxy": d1_value,
        "D2_proxy": d2_value,
        "D3_proxy": d3_value,
        "D4_pressure_pa": d4_pressure,
        "D4_balance_ev": d4_balance,
        "flow_total_ev": flow_total,
        "D1_share": d1_value / flow_total,
        "D2_share": d2_value / flow_total,
        "D3_share": d3_value / flow_total,
        "D4_share": d4_balance / flow_total,
        "launcher_ok": launcher["dominant_grid"] == case["expected_grid"],
    }


def run_check(output_dir: str | None = None) -> dict:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    cases = [evaluate_case(case) for case in CASES]
    dense_case = next(case for case in cases if case["regime"] == "dense")
    energy_reference_ev = dense_case["D4_balance_ev"]
    energy_budget_ev = energy_reference_ev * 1.05

    pressure_ratios = [cases[index + 1]["D4_pressure_pa"] / cases[index]["D4_pressure_pa"] for index in range(len(cases) - 1)]
    expected_ratios = [density_ratio_expected(cases[index]["electron_density_m3"], cases[index + 1]["electron_density_m3"]) for index in range(len(cases) - 1)]
    pressure_scaling_ok = all(close_enough(actual, expected) for actual, expected in zip(pressure_ratios, expected_ratios))
    launcher_ok = all(case["launcher_ok"] for case in cases)
    atomic_ok = cases[0]["D1_share"] > 0.95 and cases[0]["D4_share"] < 1.0e-3
    metal_ok = cases[1]["D1_share"] > cases[1]["D2_share"] > 0.0 and cases[1]["D4_share"] < 0.5
    lanthanide_ok = cases[2]["D3_share"] > 0.2 and cases[2]["D3_proxy"] > cases[2]["D2_proxy"]
    dense_ok = cases[3]["D4_share"] > 0.9 and cases[3]["D1_share"] < 0.05
    budget_ok = all(case["flow_total_ev"] <= energy_budget_ev for case in cases)
    verdict = "supported" if pressure_scaling_ok and launcher_ok and atomic_ok and metal_ok and lanthanide_ok and dense_ok and budget_ok else "contradicted"

    payload = {
        "timestamp": timestamp,
        "suite": "regime_physics",
        "regime": "flow",
        "verdict": verdict,
        "hypothesis": "The D1 / D2 / D3 / D4 grid stays ordered across atomic, metallic, lanthanide, and dense regimes",
        "case_control": "Na atomic, Al metallic, Ce lanthanide, and Pb dense reference",
        "observable": "Relative D1, D2, D3, and D4 shares plus the pressure n_e^(5/3) scaling",
        "checks": ["atomic D1 dominance", "metal D1 + D2 visibility", "lanthanide D3 necessity", "dense D4 dominance", "pressure scaling", "launcher routes each branch correctly"],
        "pressure_scaling_ok": pressure_scaling_ok,
        "launcher_ok": launcher_ok,
        "atomic_ok": atomic_ok,
        "metal_ok": metal_ok,
        "lanthanide_ok": lanthanide_ok,
        "dense_ok": dense_ok,
        "budget_ok": budget_ok,
        "energy_reference_ev": energy_reference_ev,
        "energy_budget_ev": energy_budget_ev,
        "cases": cases,
        "pressure_ratios": pressure_ratios,
        "expected_pressure_ratios": expected_ratios,
    }
    json_path, txt_path = write_report("Regime flow check", "regime_flow_check", payload, output_dir)
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the D1 / D2 / D3 / D4 flow plan across representative regimes.")
    parser.add_argument("--output-dir", default=None, help="Directory for the regime report")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()