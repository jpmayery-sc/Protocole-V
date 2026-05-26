"""Check the V12 fine-correction bounds."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v10spectre_check import spectral_correction
from v10spectre_check import SPECTRE_CASES
from v8level_check import evaluate_level_shift


FINE_CASES = [
    {"name": "H", "z": 1, "n": 2},
    {"name": "He", "z": 2, "n": 2},
    {"name": "Fe", "z": 26, "n": 2},
    {"name": "Xe", "z": 54, "n": 2},
    {"name": "Pb", "z": 82, "n": 2},
    {"name": "U", "z": 92, "n": 2},
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def evaluate_fine_bounds() -> dict:
    level_result = evaluate_level_shift()
    alpha_ref = level_result["alpha_ref"]
    base_delta_phi = level_result["base_delta_phi"]

    cases = []
    for case in FINE_CASES:
        correction = spectral_correction(case["z"], case["n"], alpha_ref, base_delta_phi)
        cases.append(
            {
                "name": case["name"],
                "z": case["z"],
                "n": case["n"],
                "correction": correction,
            }
        )

    absolute_band_ok = all(1.0e-6 <= abs(case["correction"]) <= 1.0e-3 for case in cases)
    monotone_ok = all(later["correction"] > earlier["correction"] for earlier, later in zip(cases, cases[1:]))
    fe_index = next(index for index, case in enumerate(cases) if case["name"] == "Fe")
    fe_stable_ok = cases[fe_index]["correction"] < 5.0e-4 and (cases[fe_index + 1]["correction"] / cases[fe_index]["correction"]) < 10.0
    verdict = "conforme" if absolute_band_ok and monotone_ok and fe_stable_ok else "falsifie"

    return {
        "alpha_ref": alpha_ref,
        "base_delta_phi": base_delta_phi,
        "cases": cases,
        "absolute_band_ok": absolute_band_ok,
        "monotone_ok": monotone_ok,
        "fe_stable_ok": fe_stable_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_fine_bounds()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "les corrections fines doivent rester dans une plage realiste et suivre une hierarchie avec Z",
        "case_control": "H, He, Fe, Xe, Pb, U",
        "observable": "DeltaE_torsion(Z)",
        "expected": "amplitude entre 10^-6 et 10^-3 eV et croissance avec Z",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "base_delta_phi": result["base_delta_phi"],
            "absolute_band_ok": result["absolute_band_ok"],
            "monotone_ok": result["monotone_ok"],
            "fe_stable_ok": result["fe_stable_ok"],
        },
        "cases": result["cases"],
        "verdict": result["verdict"],
        "reference": "V8 level shift and V10 spectral corrections",
    }

    json_path = outdir / f"v12fine_check_{timestamp}.json"
    txt_path = outdir / f"v12fine_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V12 fine bounds check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"absolute_band_ok: {result['absolute_band_ok']}",
        f"monotone_ok: {result['monotone_ok']}",
        f"fe_stable_ok: {result['fe_stable_ok']}",
        "",
        "Cases:",
    ]
    for case in result["cases"]:
        lines.append(f"- {case['name']}: Z={case['z']} n={case['n']} correction={case['correction']:.6e}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check V12 fine-correction bounds.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()