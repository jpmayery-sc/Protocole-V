"""Check the V7-GEO geodesic behavior in D2."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from alphageometricport_check import evaluate_geometric_port


ALPHA_SAMPLES = [
    {"name": "alpha_ref", "alpha": 1.0 / 137.035999084},
    {"name": "alpha_mid", "alpha": (1.0 / 137.035999084 + 1.0 / 137.0) / 2.0},
    {"name": "alpha_approx", "alpha": 1.0 / 137.0},
    {"name": "alpha_high", "alpha": 1.0 / 128.0},
]

R_TRACK = 1.0
B_IMPACT = 1.5
THETA_SAMPLES = [0.25, 0.5, 1.0]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_geodesics() -> dict:
    alpha_reference = evaluate_geometric_port()["alpha_ref"]
    geodesic_samples = []

    for entry in ALPHA_SAMPLES:
        alpha = entry["alpha"]
        beta = 1.0 - alpha
        theta_track = math.atan(R_TRACK / B_IMPACT) / beta
        precession = 2.0 * math.pi * (1.0 / beta - 1.0)
        radial_profile = [B_IMPACT * math.tan(beta * theta_sample) for theta_sample in THETA_SAMPLES]
        geodesic_samples.append(
            {
                "name": entry["name"],
                "alpha": alpha,
                "beta": beta,
                "theta_track": theta_track,
                "precession_rad": precession,
                "radial_profile": radial_profile,
            }
        )

    theta_track_values = [sample["theta_track"] for sample in geodesic_samples]
    precession_values = [sample["precession_rad"] for sample in geodesic_samples]
    radial_by_theta = list(zip(*[sample["radial_profile"] for sample in geodesic_samples]))

    trajectory_monotone_ok = all(later > earlier for earlier, later in zip(theta_track_values, theta_track_values[1:]))
    precession_monotone_ok = all(later > earlier for earlier, later in zip(precession_values, precession_values[1:]))
    precession_positive_ok = all(value > 0.0 for value in precession_values)
    radial_monotone_ok = all(all(later < earlier for earlier, later in zip(profile, profile[1:])) for profile in radial_by_theta)
    radial_small_ok = max(max(profile) - min(profile) for profile in radial_by_theta) < 0.01
    delta_theta = evaluate_geometric_port()["delta_Dtheta_rad"]
    delta_theta_consistent_ok = math.isclose(delta_theta, 2.0 * math.pi * (alpha_reference - 1.0 / 137.0), rel_tol=0.0, abs_tol=1.0e-15)

    verdict = "conforme" if (
        trajectory_monotone_ok
        and precession_monotone_ok
        and precession_positive_ok
        and radial_monotone_ok
        and radial_small_ok
        and delta_theta_consistent_ok
    ) else "rejette"

    return {
        "alpha_samples": ALPHA_SAMPLES,
        "geodesic_samples": geodesic_samples,
        "theta_track_values": theta_track_values,
        "precession_values": precession_values,
        "trajectory_monotone_ok": trajectory_monotone_ok,
        "precession_monotone_ok": precession_monotone_ok,
        "precession_positive_ok": precession_positive_ok,
        "radial_monotone_ok": radial_monotone_ok,
        "radial_small_ok": radial_small_ok,
        "delta_theta_consistent_ok": delta_theta_consistent_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_geodesics()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "une variation de alpha modifie les geodesiques en D2",
        "case_control": "alpha_ref, alpha_mid, alpha_approx, alpha_high",
        "observable": "theta_track, precession, radial_profile",
        "expected": "variation monotone avec precession positive et deviation radiale structuree",
        "measured": {
            "trajectory_monotone_ok": result["trajectory_monotone_ok"],
            "precession_monotone_ok": result["precession_monotone_ok"],
            "precession_positive_ok": result["precession_positive_ok"],
            "radial_monotone_ok": result["radial_monotone_ok"],
            "radial_small_ok": result["radial_small_ok"],
            "delta_theta_consistent_ok": result["delta_theta_consistent_ok"],
        },
        "samples": result["geodesic_samples"],
        "verdict": result["verdict"],
        "reference": "V5-G alpha gate with D2 conical transport",
    }

    json_path = outdir / f"v7geo_check_{timestamp}.json"
    txt_path = outdir / f"v7geo_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V7 GEO check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"trajectory_monotone_ok: {result['trajectory_monotone_ok']}",
        f"precession_monotone_ok: {result['precession_monotone_ok']}",
        f"precession_positive_ok: {result['precession_positive_ok']}",
        f"radial_monotone_ok: {result['radial_monotone_ok']}",
        f"radial_small_ok: {result['radial_small_ok']}",
        f"delta_theta_consistent_ok: {result['delta_theta_consistent_ok']}",
        "",
        "Samples:",
    ]
    for sample in result["geodesic_samples"]:
        lines.append(
            f"- {sample['name']}: alpha={sample['alpha']:.15f} beta={sample['beta']:.15f} theta_track={sample['theta_track']:.15f} precession={sample['precession_rad']:.15f}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V7 GEO geodesic behavior in D2.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()