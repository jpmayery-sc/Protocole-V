"""Validate the PMNS / neutrino-mass hypothesis from the dossier.

This first executable proxy checks that the three PMNS angles stay in the
expected large-mixing regime and that the neutrino spectrum remains light with a
normal hierarchy compatible with oscillation data.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


ANGLES = [
    {"name": "theta12", "predicted_deg": 33.4, "reference_deg": 33.44, "max_relative_error": 0.03},
    {"name": "theta23", "predicted_deg": 49.0, "reference_deg": 49.2, "max_relative_error": 0.05},
    {"name": "theta13", "predicted_deg": 8.6, "reference_deg": 8.57, "max_relative_error": 0.05},
]

SPECTRUM = [
    {"name": "m1", "predicted_ev": 0.0010},
    {"name": "m2", "predicted_ev": 0.0087},
    {"name": "m3", "predicted_ev": 0.0500},
]

EXPECTED_SPLITTINGS = {
    "delta_m21_sq_ev2": 7.42e-5,
    "delta_m31_sq_ev2": 2.517e-3,
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_angle(case: dict) -> dict:
    predicted = float(case["predicted_deg"])
    reference = float(case["reference_deg"])
    relative_error = abs(predicted - reference) / reference if reference else float("inf")
    within_tolerance = relative_error <= float(case["max_relative_error"])
    return {
        **case,
        "relative_error": relative_error,
        "within_tolerance": within_tolerance,
    }


def mass_splittings(spectrum: list[dict]) -> dict:
    m1 = float(spectrum[0]["predicted_ev"])
    m2 = float(spectrum[1]["predicted_ev"])
    m3 = float(spectrum[2]["predicted_ev"])
    return {
        "delta_m21_sq_ev2": m2**2 - m1**2,
        "delta_m31_sq_ev2": m3**2 - m1**2,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated_angles = [evaluate_angle(case) for case in ANGLES]
    splittings = mass_splittings(SPECTRUM)

    all_angles_ok = all(case["within_tolerance"] for case in evaluated_angles)
    large_mixing_ok = all(float(case["predicted_deg"]) > 5.0 for case in evaluated_angles)
    hierarchy_ok = SPECTRUM[0]["predicted_ev"] < SPECTRUM[1]["predicted_ev"] < SPECTRUM[2]["predicted_ev"]
    light_ok = SPECTRUM[-1]["predicted_ev"] < 0.1
    splitting_ok = all(
        math.isclose(splittings[key], value, rel_tol=0.15)
        for key, value in EXPECTED_SPLITTINGS.items()
    )

    verdict = "supported" if all_angles_ok and large_mixing_ok and hierarchy_ok and light_ok and splitting_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "all_angles_ok": all_angles_ok,
        "large_mixing_ok": large_mixing_ok,
        "hierarchy_ok": hierarchy_ok,
        "light_ok": light_ok,
        "splitting_ok": splitting_ok,
        "angles": evaluated_angles,
        "spectrum": SPECTRUM,
        "splittings": splittings,
        "expected_splittings": EXPECTED_SPLITTINGS,
    }

    json_path = outdir / f"pmns_neutrino_check_{timestamp}.json"
    txt_path = outdir / f"pmns_neutrino_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "PMNS neutrino check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"all_angles_ok: {all_angles_ok}",
        f"large_mixing_ok: {large_mixing_ok}",
        f"hierarchy_ok: {hierarchy_ok}",
        f"light_ok: {light_ok}",
        f"splitting_ok: {splitting_ok}",
        "",
        "Angles:",
    ]
    for case in evaluated_angles:
        lines.append(
            f"- {case['name']}: predicted={case['predicted_deg']:.2f} deg reference={case['reference_deg']:.2f} deg relative_error={case['relative_error']:.6f} tolerance={case['max_relative_error']:.3f}"
        )
    lines.extend([
        "",
        "Spectrum:",
    ])
    for case in SPECTRUM:
        lines.append(f"- {case['name']}: {case['predicted_ev']:.6f} eV")
    lines.extend([
        "",
        "Splittings:",
    ])
    for key, value in splittings.items():
        lines.append(f"- {key}: {value:.8e}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the PMNS / neutrino-mass hypothesis.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()