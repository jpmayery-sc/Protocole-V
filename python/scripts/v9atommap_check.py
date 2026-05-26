"""Build a reduced atomic map from the V8/V9 blocks."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v8level_check import evaluate_level_shift
from v8rayon_check import evaluate_radius_effect
from v9crit_check import band_for_z, radius_proxy, stability_score, build_kappa_lookup, evaluate_critical_regime
from v9fine_check import delta_energy


ATOM_MAP = [
    {"symbol": "H", "z": 1},
    {"symbol": "He", "z": 2},
    {"symbol": "C", "z": 6},
    {"symbol": "O", "z": 8},
    {"symbol": "Fe", "z": 26},
    {"symbol": "Pb", "z": 82},
    {"symbol": "U", "z": 92},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_atom_map() -> dict:
    critical_result = evaluate_critical_regime()
    level_result = evaluate_level_shift()
    radius_result = evaluate_radius_effect()
    kappa_lookup = build_kappa_lookup()
    alpha_ref = level_result["alpha_ref"]
    base_delta_phi = level_result["base_delta_phi"]

    rows = []
    for entry in ATOM_MAP:
        z_value = entry["z"]
        row = {
            "symbol": entry["symbol"],
            "z": z_value,
            "radius_proxy": radius_proxy(z_value),
            "delta_energy": delta_energy(z_value, base_delta_phi, alpha_ref),
            "stability_score": stability_score(z_value, base_delta_phi, alpha_ref, kappa_lookup),
            "kappa_band": band_for_z(z_value),
        }
        rows.append(row)

    radius_monotone_ok = all(later["radius_proxy"] > earlier["radius_proxy"] for earlier, later in zip(rows, rows[1:]))
    level_monotone_ok = all(later["delta_energy"] > earlier["delta_energy"] for earlier, later in zip(rows, rows[1:]))
    stability_peak_ok = rows[4]["stability_score"] == max(row["stability_score"] for row in rows)
    heavy_limit_ok = rows[5]["stability_score"] < rows[4]["stability_score"] and rows[6]["stability_score"] < rows[5]["stability_score"]
    verdict = "conforme" if radius_monotone_ok and level_monotone_ok and stability_peak_ok and heavy_limit_ok and critical_result["verdict"] == "conforme" and radius_result["verdict"] == "conforme" else "rejette"

    return {
        "alpha_ref": alpha_ref,
        "base_delta_phi": base_delta_phi,
        "rows": rows,
        "radius_monotone_ok": radius_monotone_ok,
        "level_monotone_ok": level_monotone_ok,
        "stability_peak_ok": stability_peak_ok,
        "heavy_limit_ok": heavy_limit_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_atom_map()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "V4 a V9 suffisent pour construire une carte atomique qualitative",
        "case_control": "H, He, C, O, Fe, Pb, U",
        "observable": "rayon, correction de niveau, score de stabilite",
        "expected": "rayon et correction croissent avec Z, stabilite maximale vers Fe, Pb/U en zone limite",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "base_delta_phi": result["base_delta_phi"],
            "radius_monotone_ok": result["radius_monotone_ok"],
            "level_monotone_ok": result["level_monotone_ok"],
            "stability_peak_ok": result["stability_peak_ok"],
            "heavy_limit_ok": result["heavy_limit_ok"],
        },
        "rows": result["rows"],
        "verdict": result["verdict"],
        "reference": "V8 critical, fine and stability blocks",
    }

    json_path = outdir / f"v9atommap_check_{timestamp}.json"
    txt_path = outdir / f"v9atommap_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V9 atom map check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"radius_monotone_ok: {result['radius_monotone_ok']}",
        f"level_monotone_ok: {result['level_monotone_ok']}",
        f"stability_peak_ok: {result['stability_peak_ok']}",
        f"heavy_limit_ok: {result['heavy_limit_ok']}",
        "",
        "Rows:",
    ]
    for row in result["rows"]:
        lines.append(
            f"- {row['symbol']}: Z={row['z']:.0f} radius={row['radius_proxy']:.6f} delta_E={row['delta_energy']:.6e} score={row['stability_score']:.6e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the V9 reduced atomic map.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()