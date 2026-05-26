"""Check the V5-G alpha(Delta theta) geometric port."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


REFERENCE_ALPHA_INVERSE = 137.035999084


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_geometric_port() -> dict:
    alpha_ref = 1.0 / REFERENCE_ALPHA_INVERSE
    alpha_approx = 1.0 / 137.0

    delta_theta_ref = 2.0 * math.pi * alpha_ref
    delta_theta_approx = 2.0 * math.pi * alpha_approx
    delta_dtheta = delta_theta_ref - delta_theta_approx
    absolute_delta_dtheta = abs(delta_dtheta)
    relative_delta_dtheta = absolute_delta_dtheta / delta_theta_ref

    exact_claim_ok = math.isclose(alpha_ref, alpha_approx, rel_tol=0.0, abs_tol=1.0e-12)
    geometric_port_ok = relative_delta_dtheta <= 1.0e-3
    verdict = "conforme" if geometric_port_ok else "rejette"

    return {
        "alpha_ref": alpha_ref,
        "alpha_approx": alpha_approx,
        "delta_theta_ref_rad": delta_theta_ref,
        "delta_theta_approx_rad": delta_theta_approx,
        "delta_Dtheta_rad": delta_dtheta,
        "absolute_delta_Dtheta_rad": absolute_delta_dtheta,
        "relative_delta_Dtheta": relative_delta_dtheta,
        "exact_claim_ok": exact_claim_ok,
        "geometric_port_ok": geometric_port_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_geometric_port()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la porte alpha se lit comme un deficit angulaire variable en D2",
        "case_control": "alpha_ref vs 1/137",
        "observable": "deltaDtheta = 2pi(alpharef - 1/137)",
        "expected": "ecart non nul mais faible, utilisable comme seuil geometrique",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "alpha_approx": result["alpha_approx"],
            "delta_Dtheta_rad": result["delta_Dtheta_rad"],
            "delta_Dtheta_deg": result["delta_Dtheta_rad"] * 180.0 / math.pi,
        },
        "exact_claim_ok": result["exact_claim_ok"],
        "geometric_port_ok": result["geometric_port_ok"],
        "verdict": result["verdict"],
        "reference": "alpha inverse = 137.035999084",
    }

    json_path = outdir / f"alphageometricport_check_{timestamp}.json"
    txt_path = outdir / f"alphageometricport_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Alpha geometric port check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"alpha_ref: {result['alpha_ref']:.15f}",
        f"alpha_approx: {result['alpha_approx']:.15f}",
        f"delta_theta_ref_rad: {result['delta_theta_ref_rad']:.15f}",
        f"delta_theta_approx_rad: {result['delta_theta_approx_rad']:.15f}",
        f"delta_Dtheta_rad: {result['delta_Dtheta_rad']:.15f}",
        f"absolute_delta_Dtheta_rad: {result['absolute_delta_Dtheta_rad']:.15f}",
        f"relative_delta_Dtheta: {result['relative_delta_Dtheta']:.6e}",
        f"exact_claim_ok: {result['exact_claim_ok']}",
        f"geometric_port_ok: {result['geometric_port_ok']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V5-G alpha(Delta theta) geometric port.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()