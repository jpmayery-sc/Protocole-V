"""Check the V8 atomic stability frontier."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v7electronic_check import evaluate_electron_response
from v8rayon_check import evaluate_radius_effect


SPECIES_SPECS = [
    {"name": "H", "n_low": 2.0, "n_high": 3.0, "reserve": 0.60},
    {"name": "He", "n_low": 3.0, "n_high": 4.0, "reserve": 0.90},
    {"name": "Fe", "n_low": 4.0, "n_high": 5.0, "reserve": 1.00},
    {"name": "Pb", "n_low": 6.0, "n_high": 7.0, "reserve": 0.03},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def kappa_from_fit(amplitude: float, exponent: float, n_value: float) -> float:
    return amplitude * (n_value ** (-exponent))


def evaluate_stability_frontier() -> dict:
    radius_result = evaluate_radius_effect()
    electron_result = evaluate_electron_response()
    amplitude = electron_result["fit"]["amplitude"]
    exponent = electron_result["fit"]["exponent"]

    stability_samples = []
    for species in SPECIES_SPECS:
        radius_species = next(item for item in radius_result["species_results"] if item["name"] == species["name"])
        kappa_variation = abs(
            kappa_from_fit(amplitude, exponent, species["n_low"]) - kappa_from_fit(amplitude, exponent, species["n_high"])
        )
        surface_strength = radius_species["effective_radius"] / radius_species["alpha_span"]
        score = surface_strength / kappa_variation * species["reserve"]
        stability_samples.append(
            {
                "name": species["name"],
                "radius": radius_species["effective_radius"],
                "alpha_span": radius_species["alpha_span"],
                "n_low": species["n_low"],
                "n_high": species["n_high"],
                "kappa_variation": kappa_variation,
                "surface_strength": surface_strength,
                "reserve": species["reserve"],
                "score": score,
            }
        )

    scores = [sample["score"] for sample in stability_samples]
    monotone_ok = scores[0] < scores[1] < scores[2]
    fe_peak_ok = scores[2] == max(scores)
    pb_decline_ok = scores[3] < scores[2]
    positive_ok = all(score > 0.0 for score in scores)
    verdict = "conforme" if monotone_ok and fe_peak_ok and pb_decline_ok and positive_ok and radius_result["verdict"] == "conforme" and electron_result["verdict"] == "conforme" else "rejette"

    return {
        "amplitude": amplitude,
        "exponent": exponent,
        "stability_samples": stability_samples,
        "monotone_ok": monotone_ok,
        "fe_peak_ok": fe_peak_ok,
        "pb_decline_ok": pb_decline_ok,
        "positive_ok": positive_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_stability_frontier()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la stabilite atomique est controlee par la surface alpha, la variation kappa et la reserve nucleaire",
        "case_control": "H, He, Fe, Pb",
        "observable": "S(Z) = surface de stabilite / variation de kappa(n)",
        "expected": "S(H) petit, He stable, Fe maximal, Pb en declin",
        "measured": {
            "amplitude": result["amplitude"],
            "exponent": result["exponent"],
            "monotone_ok": result["monotone_ok"],
            "fe_peak_ok": result["fe_peak_ok"],
            "pb_decline_ok": result["pb_decline_ok"],
            "positive_ok": result["positive_ok"],
        },
        "stability_samples": result["stability_samples"],
        "verdict": result["verdict"],
        "reference": "V7 radius field and electron response",
    }

    json_path = outdir / f"v8stability_check_{timestamp}.json"
    txt_path = outdir / f"v8stability_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V8 stability check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"monotone_ok: {result['monotone_ok']}",
        f"fe_peak_ok: {result['fe_peak_ok']}",
        f"pb_decline_ok: {result['pb_decline_ok']}",
        f"positive_ok: {result['positive_ok']}",
        "",
        "Samples:",
    ]
    for sample in result["stability_samples"]:
        lines.append(
            f"- {sample['name']}: radius={sample['radius']:.6f} alpha_span={sample['alpha_span']:.6e} kappa_variation={sample['kappa_variation']:.6e} score={sample['score']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V8 atomic stability frontier.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()