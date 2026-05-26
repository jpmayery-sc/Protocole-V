"""Check the D1 / D4 balance in the atomic regime.

The expected result is that D1 dominates while D4 remains negligible and the
raw D4 pressure still follows the n_e^(5/3) law when the density is varied.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from d1d4_model import close_enough, d1_proxy, density_ratio_expected, fermi_balance_ev, fermi_pressure_pa


CASES = [
    {"symbol": "H", "name": "Hydrogen-like atom", "ionization_ev": 13.6, "principal_n": 1.0, "electron_density_m3": 1.0e20},
    {"symbol": "He", "name": "Helium-like atom", "ionization_ev": 24.587, "principal_n": 1.0, "electron_density_m3": 5.0e20},
    {"symbol": "Ne", "name": "Neon-like atom", "ionization_ev": 21.564, "principal_n": 2.0, "electron_density_m3": 1.0e21},
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
        "ok": d1_value > d4_balance and d4_balance / d1_value < 1.0e-3,
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
    negligible_ok = max(case["D4_over_D1"] for case in cases) < 1.0e-3
    verdict = "supported" if pressure_scaling_ok and d1_dominates_ok and negligible_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "pressure_scaling_ok": pressure_scaling_ok,
        "d1_dominates_ok": d1_dominates_ok,
        "negligible_ok": negligible_ok,
        "cases": cases,
        "pressure_ratios": pressure_ratios,
        "expected_pressure_ratios": expected_ratios,
        "regime": "atomic",
        "hypothesis": "D4 remains negligible in the atomic regime while D1 still dominates",
        "case_control": "low-density atomic ladder from H-like to Ne-like cases",
        "observable": "D1 versus D4_balance and the n_e^(5/3) scaling of the raw D4 pressure",
    }

    json_path = outdir / f"d1d4_atomic_regime_check_{timestamp}.json"
    txt_path = outdir / f"d1d4_atomic_regime_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "D1/D4 atomic regime check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"pressure_scaling_ok: {pressure_scaling_ok}",
        f"d1_dominates_ok: {d1_dominates_ok}",
        f"negligible_ok: {negligible_ok}",
        "",
        "Cases:",
    ]
    for case in cases:
        lines.append(
            f"- {case['symbol']}: n_e={case['electron_density_m3']:.3e} D1={case['D1']:.6f} D4_balance={case['D4_balance_ev']:.6e} D4_pressure={case['D4_pressure_pa']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the D1 / D4 balance in the atomic regime.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
