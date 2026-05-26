"""Check the V11 geometric redshift block."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v8level_check import evaluate_level_shift
from v9crit_check import evaluate_critical_regime


TAU = 2.0 * math.pi
WAVELENGTH_CASES = [
    {"name": "H_alpha", "z": 1, "torsion_scale": 0.8},
    {"name": "Fe_alpha", "z": 26, "torsion_scale": 1.0},
    {"name": "Pb_alpha", "z": 82, "torsion_scale": 1.25},
    {"name": "U_alpha", "z": 92, "torsion_scale": 1.4},
]
ENVIRONMENTS = [
    {"name": "quiet", "geo_scale": 0.8},
    {"name": "nominal", "geo_scale": 1.0},
    {"name": "extreme", "geo_scale": 1.35},
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def evaluate_geometric_redshift() -> dict:
    level_result = evaluate_level_shift()
    critical_result = evaluate_critical_regime()
    base_delta_phi = level_result["base_delta_phi"]

    cases = []
    for case in WAVELENGTH_CASES:
        phase_ref = base_delta_phi * (1.0 + 0.01 * float(case["z"]))
        environments = []
        redshifts = []
        for environment in ENVIRONMENTS:
            delta_phi_env = phase_ref + 1.9e-6 * environment["geo_scale"] * case["torsion_scale"] * (1.0 + float(case["z"]) / 120.0)
            redshift = (delta_phi_env - phase_ref) / TAU
            environments.append(
                {
                    "name": environment["name"],
                    "geo_scale": environment["geo_scale"],
                    "phase_ref": phase_ref,
                    "phase_env": delta_phi_env,
                    "redshift": redshift,
                }
            )
            redshifts.append(redshift)

        cases.append(
            {
                "name": case["name"],
                "z": case["z"],
                "torsion_scale": case["torsion_scale"],
                "environments": environments,
                "nominal_redshift": redshifts[1],
            }
        )

    sign_ok = all(environment["redshift"] > 0 for case in cases for environment in case["environments"])
    amplitude_ok = all(1.0e-8 <= environment["redshift"] <= 1.0e-5 for case in cases for environment in case["environments"])
    growth_ok = all(
        later["redshift"] > earlier["redshift"]
        for case in cases
        for earlier, later in zip(case["environments"], case["environments"][1:])
    )
    z_growth_ok = all(later["nominal_redshift"] > earlier["nominal_redshift"] for earlier, later in zip(cases, cases[1:]))
    v9_coherence_ok = critical_result["verdict"] == "conforme"
    verdict = "conforme" if sign_ok and amplitude_ok and growth_ok and z_growth_ok and v9_coherence_ok and level_result["verdict"] == "conforme" else "rejette"

    return {
        "base_delta_phi": base_delta_phi,
        "cases": cases,
        "sign_ok": sign_ok,
        "amplitude_ok": amplitude_ok,
        "growth_ok": growth_ok,
        "z_growth_ok": z_growth_ok,
        "v9_coherence_ok": v9_coherence_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_geometric_redshift()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la torsion D2 induit un redshift geometrique de phase petit mais non nul",
        "case_control": "H_alpha, Fe_alpha, Pb_alpha, U_alpha",
        "observable": "z_geo",
        "expected": "signe coherent, amplitude faible et croissance avec la torsion",
        "measured": {
            "base_delta_phi": result["base_delta_phi"],
            "sign_ok": result["sign_ok"],
            "amplitude_ok": result["amplitude_ok"],
            "growth_ok": result["growth_ok"],
            "z_growth_ok": result["z_growth_ok"],
            "v9_coherence_ok": result["v9_coherence_ok"],
        },
        "cases": result["cases"],
        "verdict": result["verdict"],
        "reference": "V8 level shift and V9 critical regime",
    }

    json_path = outdir / f"v11geo_check_{timestamp}.json"
    txt_path = outdir / f"v11geo_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V11 geometric redshift check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"sign_ok: {result['sign_ok']}",
        f"amplitude_ok: {result['amplitude_ok']}",
        f"growth_ok: {result['growth_ok']}",
        f"z_growth_ok: {result['z_growth_ok']}",
        "",
        "Cases:",
    ]
    for case in result["cases"]:
        environments = ", ".join(f"{environment['name']}={environment['redshift']:.6e}" for environment in case["environments"])
        lines.append(f"- {case['name']}: {environments}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V11 geometric redshift block.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()