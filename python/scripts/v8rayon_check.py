"""Check the V8 atomic radius from the V7 coupling field."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v7coupling_check import evaluate_coupling_field


E_REFERENCE = 50.0
SPECIES_SPECS = [
    {"name": "H", "z": 1.0, "n": 2.0, "candidates": [0.42, 0.48, 0.54]},
    {"name": "He", "z": 2.0, "n": 3.0, "candidates": [0.60, 0.72, 0.84]},
    {"name": "Fe", "z": 26.0, "n": 4.0, "candidates": [1.20, 1.44, 1.68]},
    {"name": "Pb", "z": 82.0, "n": 7.0, "candidates": [1.80, 2.16, 2.52]},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_radius_effect() -> dict:
    coupling = evaluate_coupling_field()
    alpha0 = coupling["alpha0"]
    aE = coupling["aE"]
    amplitude = coupling["amplitude"]
    exponent = coupling["exponent"]
    ar = coupling["ar"]

    species_results = []
    for species in SPECIES_SPECS:
        candidates = species["candidates"]
        alpha_values = []
        gradient_values = []
        for radius in candidates:
            alpha_value = alpha0 + aE * E_REFERENCE + amplitude * (species["n"] ** (-exponent)) + ar / radius
            alpha_values.append(alpha_value)
            gradient_values.append(abs(-ar / (radius**2)))

        best_index = min(range(len(candidates)), key=lambda index: gradient_values[index])
        effective_radius = candidates[best_index]
        alpha_span = max(alpha_values) - min(alpha_values)
        species_results.append(
            {
                "name": species["name"],
                "z": species["z"],
                "n": species["n"],
                "candidates": candidates,
                "alpha_values": alpha_values,
                "gradient_values": gradient_values,
                "effective_radius": effective_radius,
                "alpha_span": alpha_span,
                "gradient_min": min(gradient_values),
                "gradient_max": max(gradient_values),
                "minimum_found": effective_radius == max(candidates),
            }
        )

    h_radius = species_results[0]["effective_radius"]
    he_radius = species_results[1]["effective_radius"]
    fe_radius = species_results[2]["effective_radius"]
    pb_radius = species_results[3]["effective_radius"]

    order_ok = h_radius < he_radius < fe_radius
    pb_soft_ok = species_results[3]["gradient_min"] < species_results[2]["gradient_min"]
    span_ok = all(result["alpha_span"] < 1.0e-5 for result in species_results)
    radius_band_ok = (
        0.3 < h_radius < 1.0
        and 0.5 < he_radius < 1.2
        and 1.0 < fe_radius < 2.5
        and 1.5 < pb_radius < 3.5
    )
    minimum_ok = all(result["minimum_found"] for result in species_results)

    verdict = "conforme" if order_ok and pb_soft_ok and span_ok and radius_band_ok and minimum_ok else "rejette"

    return {
        "alpha0": alpha0,
        "aE": aE,
        "amplitude": amplitude,
        "exponent": exponent,
        "ar": ar,
        "species_results": species_results,
        "order_ok": order_ok,
        "pb_soft_ok": pb_soft_ok,
        "span_ok": span_ok,
        "radius_band_ok": radius_band_ok,
        "minimum_ok": minimum_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_radius_effect()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "le rayon atomique stable correspond a une zone ou le champ alpha(E,n,r) varie peu",
        "case_control": "H, He, Fe, Pb",
        "observable": "R_eff et la pente radiale locale du champ alpha",
        "expected": "ordre H < He < Fe, Pb mou, minimum de variation en fin de fenetre",
        "measured": {
            "alpha0": result["alpha0"],
            "aE": result["aE"],
            "amplitude": result["amplitude"],
            "exponent": result["exponent"],
            "ar": result["ar"],
            "order_ok": result["order_ok"],
            "pb_soft_ok": result["pb_soft_ok"],
            "span_ok": result["span_ok"],
            "radius_band_ok": result["radius_band_ok"],
            "minimum_ok": result["minimum_ok"],
        },
        "species_results": result["species_results"],
        "verdict": result["verdict"],
        "reference": "V7 coupling field alpha(E,n,r)",
    }

    json_path = outdir / f"v8rayon_check_{timestamp}.json"
    txt_path = outdir / f"v8rayon_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V8 radius check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"order_ok: {result['order_ok']}",
        f"pb_soft_ok: {result['pb_soft_ok']}",
        f"span_ok: {result['span_ok']}",
        f"radius_band_ok: {result['radius_band_ok']}",
        f"minimum_ok: {result['minimum_ok']}",
        "",
        "Species:",
    ]
    for species in result["species_results"]:
        lines.append(
            f"- {species['name']}: R_eff={species['effective_radius']:.6f} alpha_span={species['alpha_span']:.6e} gradient_min={species['gradient_min']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V8 atomic radius from the V7 coupling field.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()