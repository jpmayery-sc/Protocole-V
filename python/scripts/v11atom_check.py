"""Check the V11 internal atomic redshift block."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v8level_check import evaluate_level_shift


ATOM_CASES = [
    {"name": "H", "z": 1, "transition_energy": 1.89},
    {"name": "He", "z": 2, "transition_energy": 2.20},
    {"name": "Fe", "z": 26, "transition_energy": 2.10},
    {"name": "Pb", "z": 82, "transition_energy": 2.35},
    {"name": "U", "z": 92, "transition_energy": 2.40},
]
ENVIRONMENTS = [
    {"name": "quiet", "atom_scale": 0.75},
    {"name": "nominal", "atom_scale": 1.0},
    {"name": "extreme", "atom_scale": 1.25},
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def evaluate_internal_redshift() -> dict:
    level_result = evaluate_level_shift()
    base_delta_phi = level_result["base_delta_phi"]
    alpha_ref = level_result["alpha_ref"]

    cases = []
    for case in ATOM_CASES:
        delta_e_ref = base_delta_phi * float(case["z"]) * alpha_ref / (0.35 + 0.26 * math.sqrt(float(case["z"])))
        environments = []
        redshifts = []
        for environment in ENVIRONMENTS:
            delta_e_env = delta_e_ref * (1.0 + 0.02 * environment["atom_scale"])
            redshift = (delta_e_env - delta_e_ref) / case["transition_energy"]
            environments.append(
                {
                    "name": environment["name"],
                    "atom_scale": environment["atom_scale"],
                    "delta_e_ref": delta_e_ref,
                    "delta_e_env": delta_e_env,
                    "redshift": redshift,
                }
            )
            redshifts.append(redshift)

        cases.append(
            {
                "name": case["name"],
                "z": case["z"],
                "transition_energy": case["transition_energy"],
                "delta_e_ref": delta_e_ref,
                "environments": environments,
                "nominal_redshift": redshifts[1],
            }
        )

    amplitude_ok = all(1.0e-7 <= environment["redshift"] <= 1.0e-3 for case in cases for environment in case["environments"])
    z_growth_ok = all(later["nominal_redshift"] > earlier["nominal_redshift"] for earlier, later in zip(cases, cases[1:]))
    env_growth_ok = all(
        later["redshift"] > earlier["redshift"]
        for case in cases
        for earlier, later in zip(case["environments"], case["environments"][1:])
    )
    heavy_tail_ok = cases[2]["nominal_redshift"] < cases[3]["nominal_redshift"] < cases[4]["nominal_redshift"]
    verdict = "conforme" if amplitude_ok and z_growth_ok and env_growth_ok and heavy_tail_ok and level_result["verdict"] == "conforme" else "rejette"

    return {
        "base_delta_phi": base_delta_phi,
        "alpha_ref": alpha_ref,
        "cases": cases,
        "amplitude_ok": amplitude_ok,
        "z_growth_ok": z_growth_ok,
        "env_growth_ok": env_growth_ok,
        "heavy_tail_ok": heavy_tail_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_internal_redshift()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "les corrections de niveaux internes induisent un redshift atomique petit mais mesurable",
        "case_control": "H, He, Fe, Pb, U",
        "observable": "z_int",
        "expected": "amplitude dans la bande 10^-6 a 10^-3 et croissance avec Z",
        "measured": {
            "base_delta_phi": result["base_delta_phi"],
            "alpha_ref": result["alpha_ref"],
            "amplitude_ok": result["amplitude_ok"],
            "z_growth_ok": result["z_growth_ok"],
            "env_growth_ok": result["env_growth_ok"],
            "heavy_tail_ok": result["heavy_tail_ok"],
        },
        "cases": result["cases"],
        "verdict": result["verdict"],
        "reference": "V8 level shift and V10 spectral corrections",
    }

    json_path = outdir / f"v11atom_check_{timestamp}.json"
    txt_path = outdir / f"v11atom_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V11 atomic redshift check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"amplitude_ok: {result['amplitude_ok']}",
        f"z_growth_ok: {result['z_growth_ok']}",
        f"env_growth_ok: {result['env_growth_ok']}",
        f"heavy_tail_ok: {result['heavy_tail_ok']}",
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
    parser = argparse.ArgumentParser(description="Check the V11 internal atomic redshift block.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()