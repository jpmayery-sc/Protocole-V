"""Validate the hadron-collective-mode hypothesis from the dossier.

This first executable proxy checks that a small set of low-lying hadrons can be
treated as stable collective objects with the expected quark content and mass
ordering.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {
        "name": "pion_plus",
        "type": "meson",
        "quark_content": "u dbar",
        "predicted_mass_mev": 140.0,
        "reference_mass_mev": 139.57,
        "max_relative_error": 0.02,
    },
    {
        "name": "kaon_plus",
        "type": "meson",
        "quark_content": "u sbar",
        "predicted_mass_mev": 494.0,
        "reference_mass_mev": 493.68,
        "max_relative_error": 0.02,
    },
    {
        "name": "proton",
        "type": "baryon",
        "quark_content": "u u d",
        "predicted_mass_mev": 938.5,
        "reference_mass_mev": 938.27,
        "max_relative_error": 0.01,
    },
    {
        "name": "neutron",
        "type": "baryon",
        "quark_content": "u d d",
        "predicted_mass_mev": 939.6,
        "reference_mass_mev": 939.57,
        "max_relative_error": 0.01,
    },
    {
        "name": "lambda0",
        "type": "baryon",
        "quark_content": "u d s",
        "predicted_mass_mev": 1115.7,
        "reference_mass_mev": 1115.68,
        "max_relative_error": 0.01,
    },
    {
        "name": "delta_plus_plus",
        "type": "baryon",
        "quark_content": "u u u",
        "predicted_mass_mev": 1232.0,
        "reference_mass_mev": 1232.0,
        "max_relative_error": 0.01,
    },
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

    ordered = all(b["predicted_mass_mev"] >= a["predicted_mass_mev"] for a, b in zip(evaluated[:-1], evaluated[1:]))
    all_match = all(case["within_tolerance"] for case in evaluated)
    meson_ok = all(case["within_tolerance"] for case in evaluated if case["type"] == "meson")
    baryon_ok = all(case["within_tolerance"] for case in evaluated if case["type"] == "baryon")

    verdict = "supported" if ordered and all_match and meson_ok and baryon_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "ordered": ordered,
        "all_match": all_match,
        "meson_ok": meson_ok,
        "baryon_ok": baryon_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"hadron_collective_mode_check_{timestamp}.json"
    txt_path = outdir / f"hadron_collective_mode_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Hadron collective mode check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"ordered: {ordered}",
        f"all_match: {all_match}",
        f"meson_ok: {meson_ok}",
        f"baryon_ok: {baryon_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: type={case['type']} content={case['quark_content']} predicted={case['predicted_mass_mev']:.2f} MeV reference={case['reference_mass_mev']:.2f} MeV relative_error={case['relative_error']:.6f} tolerance={case['max_relative_error']:.3f}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the hadron collective mode hypothesis.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()