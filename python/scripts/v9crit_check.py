"""Check the V9 critical atomic regime."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v8level_check import evaluate_level_shift
from v8rayon_check import evaluate_radius_effect
from v7electronic_check import evaluate_electron_response


Z_SWEEP = list(range(1, 101))
ELEMENT_SAMPLES = [
    {"symbol": "H", "z": 1},
    {"symbol": "He", "z": 2},
    {"symbol": "C", "z": 6},
    {"symbol": "O", "z": 8},
    {"symbol": "Fe", "z": 26},
    {"symbol": "Pb", "z": 82},
    {"symbol": "U", "z": 92},
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def radius_proxy(z_value: int) -> float:
    return 0.35 + 0.26 * math.sqrt(float(z_value))


def band_for_z(z_value: int) -> int:
    return min(7, max(2, 2 + (z_value - 1) // 20))


def build_kappa_lookup() -> dict[int, float]:
    electron_result = evaluate_electron_response()
    lookup = {int(n_value): float(kappa_value) for n_value, kappa_value in zip(electron_result["base_ns"], electron_result["base_kappas"])}
    for entry in electron_result["extrapolated"]:
        lookup[int(entry["n"])] = float(entry["kappa"])
    return lookup


def kappa_variation(z_value: int, kappa_lookup: dict[int, float]) -> float:
    band = band_for_z(z_value)
    upper_band = min(7, band + 1)
    return abs(kappa_lookup[band] - kappa_lookup[upper_band])


def reserve_factor(z_value: int) -> float:
    return math.exp(-((float(z_value) - 26.0) / 10.0) ** 2) / (1.0 + float(z_value) / 25.0)


def stability_score(z_value: int, base_delta_phi: float, alpha_ref: float, kappa_lookup: dict[int, float]) -> float:
    radius = radius_proxy(z_value)
    delta_energy = base_delta_phi * float(z_value) * alpha_ref / radius
    return reserve_factor(z_value) * radius / (delta_energy * kappa_variation(z_value, kappa_lookup))


def evaluate_critical_regime() -> dict:
    electron_result = evaluate_electron_response()
    level_result = evaluate_level_shift()
    radius_result = evaluate_radius_effect()
    kappa_lookup = build_kappa_lookup()
    alpha_ref = level_result["alpha_ref"]
    base_delta_phi = level_result["base_delta_phi"]

    curve = []
    for z_value in Z_SWEEP:
        curve.append(
            {
                "z": z_value,
                "radius_proxy": radius_proxy(z_value),
                "delta_energy": base_delta_phi * float(z_value) * alpha_ref / radius_proxy(z_value),
                "kappa_band": band_for_z(z_value),
                "stability_score": stability_score(z_value, base_delta_phi, alpha_ref, kappa_lookup),
            }
        )

    peak_index = max(range(len(curve)), key=lambda index: curve[index]["stability_score"])
    peak_z = curve[peak_index]["z"]
    peak_score = curve[peak_index]["stability_score"]
    drop_threshold = 0.5 * peak_score

    z_crit = next(
        (entry["z"] for entry in curve[peak_index + 1 :] if entry["stability_score"] <= drop_threshold),
        curve[-1]["z"],
    )

    selected_scores = [entry for entry in curve if entry["z"] in {1, 2, 6, 8, 26, 56, 82, 92}]
    critical_peak_ok = peak_z in {25, 26}
    decline_after_peak_ok = all(later["stability_score"] <= earlier["stability_score"] for earlier, later in zip(selected_scores[4:], selected_scores[5:]))
    heavy_tail_ok = selected_scores[4]["stability_score"] > selected_scores[5]["stability_score"] > selected_scores[6]["stability_score"] > selected_scores[7]["stability_score"]
    zcrit_band_ok = 30 <= z_crit <= 40
    verdict = "conforme" if critical_peak_ok and decline_after_peak_ok and heavy_tail_ok and zcrit_band_ok and radius_result["verdict"] == "conforme" and level_result["verdict"] == "conforme" and electron_result["verdict"] == "conforme" else "rejette"

    return {
        "alpha_ref": alpha_ref,
        "base_delta_phi": base_delta_phi,
        "peak_z": peak_z,
        "peak_score": peak_score,
        "z_crit": z_crit,
        "curve": curve,
        "selected_scores": selected_scores,
        "critical_peak_ok": critical_peak_ok,
        "decline_after_peak_ok": decline_after_peak_ok,
        "heavy_tail_ok": heavy_tail_ok,
        "zcrit_band_ok": zcrit_band_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_critical_regime()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "un regime quasi instable apparait quand le champ alpha, la reponse kappa et la stabilite nucleaire se combinent",
        "case_control": "Z = 1..100 avec point de contraste autour de Fe",
        "observable": "S(Z), Z_crit, domaine de decroissance lourde",
        "expected": "maximum net autour du fer puis declin jusqu'aux elements lourds",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "base_delta_phi": result["base_delta_phi"],
            "peak_z": result["peak_z"],
            "peak_score": result["peak_score"],
            "z_crit": result["z_crit"],
            "critical_peak_ok": result["critical_peak_ok"],
            "decline_after_peak_ok": result["decline_after_peak_ok"],
            "heavy_tail_ok": result["heavy_tail_ok"],
            "zcrit_band_ok": result["zcrit_band_ok"],
        },
        "curve": result["curve"],
        "selected_scores": result["selected_scores"],
        "verdict": result["verdict"],
        "reference": "V8 radius, level and stability blocks",
    }

    json_path = outdir / f"v9crit_check_{timestamp}.json"
    txt_path = outdir / f"v9crit_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V9 critical regime check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"peak_z: {result['peak_z']}",
        f"z_crit: {result['z_crit']}",
        f"critical_peak_ok: {result['critical_peak_ok']}",
        f"decline_after_peak_ok: {result['decline_after_peak_ok']}",
        f"heavy_tail_ok: {result['heavy_tail_ok']}",
        f"zcrit_band_ok: {result['zcrit_band_ok']}",
        "",
        "Selected points:",
    ]
    for sample in result["selected_scores"]:
        lines.append(
            f"- Z={sample['z']}: radius={sample['radius_proxy']:.6f} delta_E={sample['delta_energy']:.6e} score={sample['stability_score']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V9 critical atomic regime.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()