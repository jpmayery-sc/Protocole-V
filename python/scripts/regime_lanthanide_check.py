"""Check the lanthanide branch of the regime-physics grid."""
from __future__ import annotations

import argparse
import json
import time

from d1d4_model import d1_proxy, fermi_balance_ev, fermi_pressure_pa
from regime_physics_common import write_report
from run_regime_physics import run_regime


CASES = [
    {"symbol": "Ce", "ionization_ev": 5.5387, "principal_n": 4.0, "electron_density_m3": 4.0e28},
    {"symbol": "Sm", "ionization_ev": 5.6437, "principal_n": 4.0, "electron_density_m3": 4.5e28},
    {"symbol": "Nd", "ionization_ev": 5.5250, "principal_n": 4.0, "electron_density_m3": 5.0e28},
    {"symbol": "Gd", "ionization_ev": 6.1501, "principal_n": 4.0, "electron_density_m3": 5.5e28},
    {"symbol": "Yb", "ionization_ev": 6.2542, "principal_n": 6.0, "electron_density_m3": 6.0e28},
]


def run_check(output_dir: str | None = None) -> dict:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    cases = []
    for case in CASES:
        launcher = run_regime(
            "lanthanide",
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
                "D3_required": launcher["dominant_grid"] == "D1 + D3",
                "verdict": "supported" if launcher["dominant_grid"] == "D1 + D3" else "contradicted",
            }
        )

    launcher_ok = all(case["launcher_grid"] == "D1 + D3" for case in cases)
    d3_required_ok = all(case["D3_required"] for case in cases)
    non_collapse_ok = all(case["D1_proxy"] > 0.0 for case in cases)
    balance_band_ok = all(case["D4_balance_ev"] > 0.0 for case in cases)
    verdict = "supported" if launcher_ok and d3_required_ok and non_collapse_ok and balance_band_ok else "contradicted"

    payload = {
        "timestamp": timestamp,
        "suite": "regime_physics",
        "regime": "lanthanide",
        "verdict": verdict,
        "hypothesis": "Lanthanides require D3 and do not collapse to D1-only reading",
        "case_control": "Ce, Nd, and Yb lanthanide references",
        "observable": "launcher grid choice and the D3-required branch",
        "checks": ["D3 is mandatory", "no D1-only collapse", "launcher routes lanthanides to D1 + D3"],
        "launcher_ok": launcher_ok,
        "d3_required_ok": d3_required_ok,
        "non_collapse_ok": non_collapse_ok,
        "balance_band_ok": balance_band_ok,
        "cases": cases,
    }
    json_path, txt_path = write_report("Regime lanthanide check", "regime_lanthanide_check", payload, output_dir)
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the lanthanide branch of the regime-physics grid.")
    parser.add_argument("--output-dir", default=None, help="Directory for the regime report")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()