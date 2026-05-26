"""Validate the skin effect trend across a few representative conductor cases.

The check uses the standard skin-depth approximation:

    delta = sqrt(2 * rho / (mu * omega))

and verifies that the penetration depth decreases as frequency increases.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


MU0 = 4.0 * math.pi * 1.0e-7

CASES = [
    {"name": "Cu low", "resistivity_ohm_m": 1.68e-8, "relative_mu": 1.0, "frequency_hz": 1.0e3},
    {"name": "Cu mid", "resistivity_ohm_m": 1.68e-8, "relative_mu": 1.0, "frequency_hz": 1.0e5},
    {"name": "Cu high", "resistivity_ohm_m": 1.68e-8, "relative_mu": 1.0, "frequency_hz": 1.0e7},
    {"name": "Fe low", "resistivity_ohm_m": 9.71e-8, "relative_mu": 200.0, "frequency_hz": 1.0e3},
    {"name": "Fe high", "resistivity_ohm_m": 9.71e-8, "relative_mu": 200.0, "frequency_hz": 1.0e7},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def skin_depth(resistivity_ohm_m: float, relative_mu: float, frequency_hz: float) -> float:
    omega = 2.0 * math.pi * frequency_hz
    return math.sqrt((2.0 * resistivity_ohm_m) / (MU0 * relative_mu * omega))


def evaluate_case(case: dict) -> dict:
    depth_m = skin_depth(case["resistivity_ohm_m"], case["relative_mu"], case["frequency_hz"])
    return {
        **case,
        "angular_frequency_rad_s": 2.0 * math.pi * case["frequency_hz"],
        "skin_depth_m": depth_m,
        "skin_depth_mm": depth_m * 1.0e3,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    cu_depths = [case["skin_depth_m"] for case in evaluated if case["name"].startswith("Cu")]
    fe_depths = [case["skin_depth_m"] for case in evaluated if case["name"].startswith("Fe")]
    cu_monotone = all(b < a for a, b in zip(cu_depths[:-1], cu_depths[1:]))
    fe_monotone = len(fe_depths) >= 2 and all(b < a for a, b in zip(fe_depths[:-1], fe_depths[1:]))
    material_contrast_ok = fe_depths[0] < cu_depths[0]

    verdict = "supported" if cu_monotone and fe_monotone and material_contrast_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "cu_monotone": cu_monotone,
        "fe_monotone": fe_monotone,
        "material_contrast_ok": material_contrast_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"skin_effect_check_{timestamp}.json"
    txt_path = outdir / f"skin_effect_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Skin effect check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"cu_monotone: {cu_monotone}",
        f"fe_monotone: {fe_monotone}",
        f"material_contrast_ok: {material_contrast_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: f={case['frequency_hz']:.3e} Hz rho={case['resistivity_ohm_m']:.3e} mu_r={case['relative_mu']:.1f} depth_mm={case['skin_depth_mm']:.6f}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the skin effect trend.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()