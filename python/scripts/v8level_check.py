"""Check the V8 atomic level correction from D2 torsion."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from d2motionfromalphaport_check import evaluate_d2_motion
from v8rayon_check import evaluate_radius_effect


TORSION_SCALE = 1.0


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_level_shift() -> dict:
    radius_result = evaluate_radius_effect()
    d2_result = evaluate_d2_motion()
    base_delta_phi = d2_result["samples"][0]["delta_phi_ref"]
    alpha_ref = d2_result["alpha_ref"]

    level_samples = []
    for species in radius_result["species_results"]:
        delta_phi = base_delta_phi * species["z"]
        tau = alpha_ref / species["effective_radius"]
        delta_energy = TORSION_SCALE * delta_phi * tau
        level_samples.append(
            {
                "name": species["name"],
                "z": species["z"],
                "radius": species["effective_radius"],
                "delta_phi": delta_phi,
                "tau": tau,
                "delta_energy": delta_energy,
            }
        )

    energy_values = [sample["delta_energy"] for sample in level_samples]
    monotone_ok = all(later > earlier for earlier, later in zip(energy_values, energy_values[1:]))
    positive_ok = all(value > 0.0 for value in energy_values)
    band_ok = all(1.0e-6 <= value <= 1.0e-3 for value in energy_values)
    fe_peak_ok = level_samples[0]["delta_energy"] < level_samples[1]["delta_energy"] < level_samples[2]["delta_energy"]
    verdict = "conforme" if monotone_ok and positive_ok and band_ok and fe_peak_ok and radius_result["verdict"] == "conforme" and d2_result["verdict"] == "conforme" else "rejette"

    return {
        "base_delta_phi": base_delta_phi,
        "alpha_ref": alpha_ref,
        "level_samples": level_samples,
        "monotone_ok": monotone_ok,
        "positive_ok": positive_ok,
        "band_ok": band_ok,
        "fe_peak_ok": fe_peak_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_level_shift()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la torsion D2 et la porte alpha induisent une correction d'energie analogue a une fine structure",
        "case_control": "H, He, Fe, Pb",
        "observable": "delta E_torsion = C * delta_phi * tau(r)",
        "expected": "delta E non nul, croissant avec Z, amplitude dans 10^-6 a 10^-3 eV",
        "measured": {
            "base_delta_phi": result["base_delta_phi"],
            "alpha_ref": result["alpha_ref"],
            "monotone_ok": result["monotone_ok"],
            "positive_ok": result["positive_ok"],
            "band_ok": result["band_ok"],
            "fe_peak_ok": result["fe_peak_ok"],
        },
        "level_samples": result["level_samples"],
        "verdict": result["verdict"],
        "reference": "V6-D2 motion and V7 radius field",
    }

    json_path = outdir / f"v8level_check_{timestamp}.json"
    txt_path = outdir / f"v8level_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V8 level check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"monotone_ok: {result['monotone_ok']}",
        f"positive_ok: {result['positive_ok']}",
        f"band_ok: {result['band_ok']}",
        f"fe_peak_ok: {result['fe_peak_ok']}",
        "",
        "Samples:",
    ]
    for sample in result["level_samples"]:
        lines.append(
            f"- {sample['name']}: Z={sample['z']:.0f} radius={sample['radius']:.6f} delta_phi={sample['delta_phi']:.6e} tau={sample['tau']:.6e} delta_E={sample['delta_energy']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V8 level correction from D2 torsion.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()