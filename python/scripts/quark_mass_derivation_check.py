"""Validate the quark-mass derivation claimed in Electron-5.

The check compares the masses stated in the dossier against reference values
and verifies that the proposed internal hierarchy remains ordered and close to
the expected scale for each quark family.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {"name": "u", "predicted_mass_mev": 2.5, "reference_mass_mev": 2.2, "max_relative_error": 0.15},
    {"name": "d", "predicted_mass_mev": 4.5, "reference_mass_mev": 4.7, "max_relative_error": 0.10},
    {"name": "s", "predicted_mass_mev": 95.0, "reference_mass_mev": 93.0, "max_relative_error": 0.05},
    {"name": "c", "predicted_mass_mev": 1270.0, "reference_mass_mev": 1270.0, "max_relative_error": 0.01},
    {"name": "b", "predicted_mass_mev": 4200.0, "reference_mass_mev": 4180.0, "max_relative_error": 0.01},
    {"name": "t", "predicted_mass_mev": 173000.0, "reference_mass_mev": 172760.0, "max_relative_error": 0.005},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    predicted = float(case["predicted_mass_mev"])
    reference = float(case["reference_mass_mev"])
    relative_error = abs(predicted - reference) / reference if reference else float("inf")
    within_tolerance = relative_error <= float(case["max_relative_error"])
    return {
        **case,
        "relative_error": relative_error,
        "within_tolerance": within_tolerance,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    ordered = all(b["predicted_mass_mev"] > a["predicted_mass_mev"] for a, b in zip(evaluated[:-1], evaluated[1:]))
    tolerance_ok = all(case["within_tolerance"] for case in evaluated)
    light_ok = all(case["relative_error"] <= case["max_relative_error"] for case in evaluated[:3])
    heavy_ok = all(case["relative_error"] <= case["max_relative_error"] for case in evaluated[3:])

    verdict = "supported" if ordered and tolerance_ok and light_ok and heavy_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "ordered": ordered,
        "tolerance_ok": tolerance_ok,
        "light_ok": light_ok,
        "heavy_ok": heavy_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"quark_mass_derivation_check_{timestamp}.json"
    txt_path = outdir / f"quark_mass_derivation_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Quark mass derivation check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"ordered: {ordered}",
        f"tolerance_ok: {tolerance_ok}",
        f"light_ok: {light_ok}",
        f"heavy_ok: {heavy_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: predicted={case['predicted_mass_mev']:.3f} MeV reference={case['reference_mass_mev']:.3f} MeV relative_error={case['relative_error']:.6f} tolerance={case['max_relative_error']:.3f}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the quark mass derivation claimed in Electron-5.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()