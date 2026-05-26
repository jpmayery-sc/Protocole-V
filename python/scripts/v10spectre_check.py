"""Check the V10 spectral corrections with torsion terms."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v7electronic_check import evaluate_electron_response
from v8level_check import evaluate_level_shift
from v9crit_check import evaluate_critical_regime


SPECTRE_CASES = [
    {"name": "H", "z": 1, "n": 2},
    {"name": "He", "z": 2, "n": 3},
    {"name": "Fe", "z": 26, "n": 4},
    {"name": "Pb", "z": 82, "n": 5},
    {"name": "U", "z": 92, "n": 6},
]
N_SERIES = [2, 3, 4, 5, 6]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def spectral_correction(z_value: int, n_value: int, alpha_ref: float, base_delta_phi: float) -> float:
    delta_phi = base_delta_phi * float(z_value)
    return 1.75 * delta_phi * alpha_ref / float(n_value**2)


def evaluate_spectral_corrections() -> dict:
    electron_result = evaluate_electron_response()
    level_result = evaluate_level_shift()
    critical_result = evaluate_critical_regime()

    alpha_ref = level_result["alpha_ref"]
    base_delta_phi = level_result["base_delta_phi"]

    series = []
    for case in SPECTRE_CASES:
        corrections = []
        levels = []
        for n_value in N_SERIES:
            correction = spectral_correction(case["z"], n_value, alpha_ref, base_delta_phi)
            rydberg_level = -13.605693 * float(case["z"] ** 2) / float(n_value**2)
            corrections.append(correction)
            levels.append(rydberg_level + correction)
        series.append(
            {
                "name": case["name"],
                "z": case["z"],
                "n_reference": case["n"],
                "corrections": corrections,
                "levels": levels,
                "correction_at_n2": corrections[0],
            }
        )

    series_monotone_ok = all(all(later < earlier for earlier, later in zip(entry["corrections"], entry["corrections"][1:])) for entry in series)
    band_ok = all(1.0e-6 <= correction <= 1.0e-3 for entry in series for correction in entry["corrections"])
    z_growth_ok = all(later["correction_at_n2"] > earlier["correction_at_n2"] for earlier, later in zip(series, series[1:]))
    v9_coherence_ok = critical_result["verdict"] == "conforme"
    electron_coherence_ok = electron_result["verdict"] == "conforme"
    verdict = "conforme" if series_monotone_ok and band_ok and z_growth_ok and v9_coherence_ok and electron_coherence_ok else "rejette"

    return {
        "alpha_ref": alpha_ref,
        "base_delta_phi": base_delta_phi,
        "series": series,
        "series_monotone_ok": series_monotone_ok,
        "band_ok": band_ok,
        "z_growth_ok": z_growth_ok,
        "v9_coherence_ok": v9_coherence_ok,
        "electron_coherence_ok": electron_coherence_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_spectral_corrections()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la torsion D2 et la porte alpha modifient les niveaux atomiques et les series spectrales",
        "case_control": "H, He, Fe, Pb, U",
        "observable": "corrections torsionnelles sur une serie de Rydberg simplifiee",
        "expected": "decrease en 1/n^2, amplitude realiste et croissance avec Z",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "base_delta_phi": result["base_delta_phi"],
            "series_monotone_ok": result["series_monotone_ok"],
            "band_ok": result["band_ok"],
            "z_growth_ok": result["z_growth_ok"],
            "v9_coherence_ok": result["v9_coherence_ok"],
        },
        "series": result["series"],
        "verdict": result["verdict"],
        "reference": "V7 electron response, V8 level shift and V9 critical regime",
    }

    json_path = outdir / f"v10spectre_check_{timestamp}.json"
    txt_path = outdir / f"v10spectre_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V10 spectral check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"series_monotone_ok: {result['series_monotone_ok']}",
        f"band_ok: {result['band_ok']}",
        f"z_growth_ok: {result['z_growth_ok']}",
        f"v9_coherence_ok: {result['v9_coherence_ok']}",
        "",
        "Series:",
    ]
    for entry in result["series"]:
        lines.append(
            f"- {entry['name']}: n2={entry['corrections'][0]:.6e} n3={entry['corrections'][1]:.6e} n4={entry['corrections'][2]:.6e} n5={entry['corrections'][3]:.6e} n6={entry['corrections'][4]:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V10 spectral corrections with torsion terms.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()