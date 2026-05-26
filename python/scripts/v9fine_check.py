"""Check the V9 extreme fine-structure corrections."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v8level_check import evaluate_level_shift
from v8rayon_check import evaluate_radius_effect
from v7electronic_check import evaluate_electron_response


HIGH_Z_CASES = [
    {"name": "Fe", "z": 26},
    {"name": "Xe", "z": 54},
    {"name": "Pb", "z": 82},
    {"name": "U", "z": 92},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def radius_proxy(z_value: int) -> float:
    return 0.35 + 0.26 * (float(z_value) ** 0.5)


def band_for_z(z_value: int) -> int:
    return min(7, max(2, 2 + (z_value - 1) // 20))


def build_kappa_lookup() -> dict[int, float]:
    electron_result = evaluate_electron_response()
    lookup = {int(n_value): float(kappa_value) for n_value, kappa_value in zip(electron_result["base_ns"], electron_result["base_kappas"])}
    for entry in electron_result["extrapolated"]:
        lookup[int(entry["n"])] = float(entry["kappa"])
    return lookup


def delta_energy(z_value: int, base_delta_phi: float, alpha_ref: float) -> float:
    return base_delta_phi * float(z_value) * alpha_ref / radius_proxy(z_value)


def fine_structure_observables() -> dict:
    level_result = evaluate_level_shift()
    radius_result = evaluate_radius_effect()
    electron_result = evaluate_electron_response()
    kappa_lookup = build_kappa_lookup()
    alpha_ref = level_result["alpha_ref"]
    base_delta_phi = level_result["base_delta_phi"]

    samples = []
    for case in HIGH_Z_CASES:
        z_value = case["z"]
        band = band_for_z(z_value)
        kappa_gap = abs(kappa_lookup[band] - kappa_lookup[min(7, band + 1)])
        correction = delta_energy(z_value, base_delta_phi, alpha_ref)
        samples.append(
            {
                "name": case["name"],
                "z": z_value,
                "band": band,
                "radius_proxy": radius_proxy(z_value),
                "delta_energy": correction,
                "kappa_gap": kappa_gap,
                "sensitivity_score": correction / kappa_gap,
            }
        )

    energy_values = [sample["delta_energy"] for sample in samples]
    monotone_ok = all(later > earlier for earlier, later in zip(energy_values, energy_values[1:]))
    band_ok = all(1.0e-6 <= value <= 1.0e-3 for value in energy_values)
    high_sensitivity_ok = samples[0]["delta_energy"] >= 1.0e-4 and samples[-1]["delta_energy"] >= 5.0e-4
    verdict = "conforme" if monotone_ok and band_ok and high_sensitivity_ok and radius_result["verdict"] == "conforme" and level_result["verdict"] == "conforme" and electron_result["verdict"] == "conforme" else "rejette"

    return {
        "alpha_ref": alpha_ref,
        "base_delta_phi": base_delta_phi,
        "samples": samples,
        "monotone_ok": monotone_ok,
        "band_ok": band_ok,
        "high_sensitivity_ok": high_sensitivity_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = fine_structure_observables()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la torsion D2, la porte alpha et le canal electronique produisent des corrections fines sensibles a Z",
        "case_control": "Fe, Xe, Pb, U",
        "observable": "delta E_torsion(Z) et sensibility score",
        "expected": "croissance reguliere et amplitude realiste dans la bande 10^-6 a 10^-3 eV",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "base_delta_phi": result["base_delta_phi"],
            "monotone_ok": result["monotone_ok"],
            "band_ok": result["band_ok"],
            "high_sensitivity_ok": result["high_sensitivity_ok"],
        },
        "samples": result["samples"],
        "verdict": result["verdict"],
        "reference": "V7 electron channel + V8 level shift",
    }

    json_path = outdir / f"v9fine_check_{timestamp}.json"
    txt_path = outdir / f"v9fine_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V9 fine corrections check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"monotone_ok: {result['monotone_ok']}",
        f"band_ok: {result['band_ok']}",
        f"high_sensitivity_ok: {result['high_sensitivity_ok']}",
        "",
        "Samples:",
    ]
    for sample in result["samples"]:
        lines.append(
            f"- {sample['name']}: Z={sample['z']:.0f} band={sample['band']} delta_E={sample['delta_energy']:.6e} sensitivity={sample['sensitivity_score']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V9 extreme fine-structure corrections.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()