"""Check the V6-D2 motion-from-alpha port."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from alphageometricport_check import evaluate_geometric_port


RADIUS_SAMPLES = [1.0, 2.0, 5.0]
K_PHI = 10.0
TAU_CRIT = 0.05
PATH_LENGTH = 2.0


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_d2_motion() -> dict:
    alpha_data = evaluate_geometric_port()
    alpha_ref = alpha_data["alpha_ref"]
    alpha_approx = alpha_data["alpha_approx"]
    delta_alpha = alpha_ref - alpha_approx

    samples = []
    for radius in RADIUS_SAMPLES:
        tau_ref = alpha_ref / radius
        tau_approx = alpha_approx / radius
        delta_tau = tau_ref - tau_approx
        delta_phi_ref = K_PHI * alpha_ref * (tau_ref / TAU_CRIT) ** 2 * PATH_LENGTH
        delta_phi_approx = K_PHI * alpha_approx * (tau_approx / TAU_CRIT) ** 2 * PATH_LENGTH
        delta_delta_phi = delta_phi_ref - delta_phi_approx
        polarization_ref = math.sin(delta_phi_ref / 2.0) ** 2
        polarization_approx = math.sin(delta_phi_approx / 2.0) ** 2
        delta_polarization = polarization_ref - polarization_approx
        samples.append(
            {
                "radius": radius,
                "tau_ref": tau_ref,
                "tau_approx": tau_approx,
                "delta_tau": delta_tau,
                "delta_phi_ref": delta_phi_ref,
                "delta_phi_approx": delta_phi_approx,
                "delta_delta_phi": delta_delta_phi,
                "polarization_ref": polarization_ref,
                "polarization_approx": polarization_approx,
                "delta_polarization": delta_polarization,
            }
        )

    delta_theta = alpha_data["delta_Dtheta_rad"]
    delta_theta_small_ok = abs(delta_theta) < 1.0e-4
    tau_shape_ok = all(sample["delta_tau"] < 0 for sample in samples)
    tau_inverse_ok = math.isclose(samples[0]["delta_tau"] / samples[1]["delta_tau"], 2.0, rel_tol=1.0e-12, abs_tol=1.0e-12) and math.isclose(samples[1]["delta_tau"] / samples[2]["delta_tau"], 2.5, rel_tol=1.0e-12, abs_tol=1.0e-12)
    effect_structured_ok = all(abs(sample["delta_delta_phi"]) > 0.0 for sample in samples) and all(abs(sample["delta_polarization"]) > 0.0 for sample in samples)
    verdict = "conforme" if delta_theta_small_ok and tau_shape_ok and tau_inverse_ok and effect_structured_ok else "rejette"

    return {
        "alpha_ref": alpha_ref,
        "alpha_approx": alpha_approx,
        "delta_alpha": delta_alpha,
        "delta_theta_rad": delta_theta,
        "delta_theta_small_ok": delta_theta_small_ok,
        "tau_shape_ok": tau_shape_ok,
        "tau_inverse_ok": tau_inverse_ok,
        "effect_structured_ok": effect_structured_ok,
        "samples": samples,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_d2_motion()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "une variation de la porte alpha se traduit en un mouvement effectif en D2",
        "case_control": "alpha_ref vs alpha_approx",
        "observable": "delta theta, delta tau, delta phi, delta P",
        "expected": "variation petite mais structuree, conserve la forme 1/r et ne sature pas",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "alpha_approx": result["alpha_approx"],
            "delta_alpha": result["delta_alpha"],
            "delta_theta_rad": result["delta_theta_rad"],
            "delta_theta_small_ok": result["delta_theta_small_ok"],
            "tau_shape_ok": result["tau_shape_ok"],
            "tau_inverse_ok": result["tau_inverse_ok"],
            "effect_structured_ok": result["effect_structured_ok"],
        },
        "samples": result["samples"],
        "verdict": result["verdict"],
        "reference": "V5-G + D2 conique / torsion / polarisation",
    }

    json_path = outdir / f"d2motionfromalphaport_check_{timestamp}.json"
    txt_path = outdir / f"d2motionfromalphaport_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "D2 motion from alpha port check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"alpha_ref: {result['alpha_ref']:.15f}",
        f"alpha_approx: {result['alpha_approx']:.15f}",
        f"delta_alpha: {result['delta_alpha']:.15e}",
        f"delta_theta_rad: {result['delta_theta_rad']:.15e}",
        f"delta_theta_small_ok: {result['delta_theta_small_ok']}",
        f"tau_shape_ok: {result['tau_shape_ok']}",
        f"tau_inverse_ok: {result['tau_inverse_ok']}",
        f"effect_structured_ok: {result['effect_structured_ok']}",
        "",
        "Samples:",
    ]
    for sample in result["samples"]:
        lines.append(
            f"- r={sample['radius']}: delta_tau={sample['delta_tau']:.15e} delta_phi_ref={sample['delta_phi_ref']:.15e} delta_phi_approx={sample['delta_phi_approx']:.15e} delta_P={sample['delta_polarization']:.15e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V6-D2 motion-from-alpha port.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()