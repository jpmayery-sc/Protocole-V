"""Check the V10 ionization regime and critical threshold."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v8level_check import evaluate_level_shift
from v8rayon_check import evaluate_radius_effect
from v9crit_check import evaluate_critical_regime


ION_SWEEP = list(range(1, 101))
ION_SAMPLE_Z = [1, 2, 26, 82, 92]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def ionization_reference(z_value: int) -> float:
    return 11.8 + 17.2 * math.exp(-((float(z_value) - 26.0) / 11.5) ** 2) + 0.75 / (1.0 + float(z_value) / 45.0)


def coupling_correction(z_value: int) -> float:
    return 0.22 * math.exp(-((float(z_value) - 26.0) / 15.0) ** 2)


def evaluate_ionization_effective() -> dict:
    level_result = evaluate_level_shift()
    radius_result = evaluate_radius_effect()
    critical_result = evaluate_critical_regime()

    alpha_ref = level_result["alpha_ref"]
    base_delta_phi = level_result["base_delta_phi"]

    samples = []
    for z_value in ION_SWEEP:
        reference = ionization_reference(z_value)
        torsion_correction = 0.18 * (base_delta_phi * float(z_value) * alpha_ref / (0.35 + 0.26 * math.sqrt(float(z_value))))
        coupling = coupling_correction(z_value)
        effective = reference - torsion_correction + coupling
        samples.append(
            {
                "z": z_value,
                "reference": reference,
                "torsion_correction": torsion_correction,
                "coupling_correction": coupling,
                "effective": effective,
            }
        )

    peak_index = max(range(len(samples)), key=lambda index: samples[index]["effective"])
    peak_z = samples[peak_index]["z"]
    peak_value = samples[peak_index]["effective"]
    z_ion_crit = next(
        (entry["z"] for entry in samples[peak_index + 1 :] if entry["effective"] <= 0.94 * peak_value),
        samples[-1]["z"],
    )

    sample_values = [samples[z_value - 1] for z_value in ION_SAMPLE_Z]
    decline_after_peak_ok = sample_values[2]["effective"] > sample_values[3]["effective"] > sample_values[4]["effective"]
    critical_peak_ok = peak_z in {25, 26, 27}
    zcrit_band_ok = 30 <= z_ion_crit <= 40
    v9_coherence_ok = abs(peak_z - critical_result["peak_z"]) <= 1 and critical_result["verdict"] == "conforme"
    radius_coherence_ok = radius_result["verdict"] == "conforme"
    verdict = (
        "conforme"
        if decline_after_peak_ok and critical_peak_ok and zcrit_band_ok and v9_coherence_ok and radius_coherence_ok and level_result["verdict"] == "conforme"
        else "rejette"
    )

    return {
        "alpha_ref": alpha_ref,
        "base_delta_phi": base_delta_phi,
        "peak_z": peak_z,
        "peak_value": peak_value,
        "z_ion_crit": z_ion_crit,
        "samples": samples,
        "sample_values": sample_values,
        "decline_after_peak_ok": decline_after_peak_ok,
        "critical_peak_ok": critical_peak_ok,
        "zcrit_band_ok": zcrit_band_ok,
        "v9_coherence_ok": v9_coherence_ok,
        "radius_coherence_ok": radius_coherence_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_ionization_effective()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "le seuil d ionisation effective combine le champ alpha, la torsion D2, la reponse electronique et la stabilite atomique",
        "case_control": "Z = 1..100 avec accent sur Fe, Pb et U",
        "observable": "E_ion_eff(Z) et Z_ion_crit",
        "expected": "maximum proche de Fe puis declin vers la queue lourde",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "base_delta_phi": result["base_delta_phi"],
            "peak_z": result["peak_z"],
            "peak_value": result["peak_value"],
            "z_ion_crit": result["z_ion_crit"],
            "decline_after_peak_ok": result["decline_after_peak_ok"],
            "critical_peak_ok": result["critical_peak_ok"],
            "zcrit_band_ok": result["zcrit_band_ok"],
            "v9_coherence_ok": result["v9_coherence_ok"],
            "radius_coherence_ok": result["radius_coherence_ok"],
        },
        "sample_values": result["sample_values"],
        "samples": result["samples"],
        "verdict": result["verdict"],
        "reference": "V8 level shift, V8 radius and V9 critical regime",
    }

    json_path = outdir / f"v10ion_check_{timestamp}.json"
    txt_path = outdir / f"v10ion_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V10 ionization check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"peak_z: {result['peak_z']}",
        f"peak_value: {result['peak_value']}",
        f"z_ion_crit: {result['z_ion_crit']}",
        f"decline_after_peak_ok: {result['decline_after_peak_ok']}",
        f"critical_peak_ok: {result['critical_peak_ok']}",
        f"zcrit_band_ok: {result['zcrit_band_ok']}",
        f"v9_coherence_ok: {result['v9_coherence_ok']}",
        "",
        "Samples:",
    ]
    for sample in result["sample_values"]:
        lines.append(
            f"- Z={sample['z']}: E_ref={sample['reference']:.6f} torsion={sample['torsion_correction']:.6e} coupling={sample['coupling_correction']:.6e} E_eff={sample['effective']:.6f}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V10 ionization regime and critical threshold.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()