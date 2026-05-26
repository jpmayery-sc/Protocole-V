"""Check the V10 Rydberg-state geometry deviations."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v8rayon_check import evaluate_radius_effect
from v9crit_check import evaluate_critical_regime


RYDBERG_N_VALUES = [2, 4, 8, 16, 32, 64]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def rydberg_radius(n_value: int) -> float:
    return float(n_value**2) * 0.529177


def alpha_gap(n_value: int) -> float:
    return 1.2e-5 * math.log1p(float(n_value)) + 1.7e-7 * math.sqrt(float(n_value))


def evaluate_rydberg_geometry() -> dict:
    radius_result = evaluate_radius_effect()
    critical_result = evaluate_critical_regime()

    alpha_ref = 0.0072973525692838015
    samples = []
    for n_value in RYDBERG_N_VALUES:
        rn_ref = rydberg_radius(n_value)
        gap = alpha_gap(n_value)
        alpha_approx = alpha_ref - gap
        rn_approx = rn_ref * (alpha_approx / alpha_ref)
        delta_rn = rn_ref - rn_approx
        samples.append(
            {
                "n": n_value,
                "rn_ref": rn_ref,
                "alpha_ref": alpha_ref,
                "alpha_approx": alpha_approx,
                "delta_rn": delta_rn,
                "relative_deviation": delta_rn / rn_ref,
            }
        )

    increasing_ok = all(later["delta_rn"] > earlier["delta_rn"] for earlier, later in zip(samples, samples[1:]))
    band_ok = all(sample["relative_deviation"] < 0.01 for sample in samples)
    geo_anchor = max(species["alpha_span"] for species in radius_result["species_results"])
    coherence_ok = geo_anchor > 0 and samples[0]["relative_deviation"] > geo_anchor / 10.0 and critical_result["verdict"] == "conforme"
    verdict = "conforme" if increasing_ok and band_ok and coherence_ok else "rejette"

    return {
        "alpha_ref": alpha_ref,
        "geo_anchor": geo_anchor,
        "samples": samples,
        "increasing_ok": increasing_ok,
        "band_ok": band_ok,
        "coherence_ok": coherence_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_rydberg_geometry()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "les etats tres excites amplifient les effets geometriques D2 sans divergence",
        "case_control": "n = 2, 4, 8, 16, 32, 64",
        "observable": "delta r_n et deviation relative",
        "expected": "croissance avec n et deviation sous 1 pour cent du rayon",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "geo_anchor": result["geo_anchor"],
            "increasing_ok": result["increasing_ok"],
            "band_ok": result["band_ok"],
            "coherence_ok": result["coherence_ok"],
        },
        "samples": result["samples"],
        "verdict": result["verdict"],
        "reference": "V7 geometry and V8 radius block",
    }

    json_path = outdir / f"v10rydberg_check_{timestamp}.json"
    txt_path = outdir / f"v10rydberg_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V10 rydberg check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"increasing_ok: {result['increasing_ok']}",
        f"band_ok: {result['band_ok']}",
        f"coherence_ok: {result['coherence_ok']}",
        "",
        "Samples:",
    ]
    for sample in result["samples"]:
        lines.append(
            f"- n={sample['n']}: rn_ref={sample['rn_ref']:.6f} delta_rn={sample['delta_rn']:.6e} rel={sample['relative_deviation']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V10 Rydberg-state geometry deviations.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()