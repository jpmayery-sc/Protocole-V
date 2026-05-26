"""Check the phase-deficit observable Delta theta = 2 pi alpha.

This script turns the alpha claim into a direct observable:
- exact claim: alpha = 1/137 exactly,
- derived observable: Delta theta = 2 pi alpha.

It reports the phase deficit in radians and degrees, and compares the exact
mnemonic value against a reference alpha inverse.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


REFERENCE_ALPHA_INVERSE = 137.035999084


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_phase_deficit() -> dict:
    exact_alpha = 1.0 / 137.0
    reference_alpha = 1.0 / REFERENCE_ALPHA_INVERSE

    exact_delta_theta = 2.0 * math.pi * exact_alpha
    reference_delta_theta = 2.0 * math.pi * reference_alpha

    absolute_delta_error = abs(exact_delta_theta - reference_delta_theta)
    relative_delta_error = absolute_delta_error / reference_delta_theta
    absolute_alpha_error = abs(exact_alpha - reference_alpha)
    relative_alpha_error = absolute_alpha_error / reference_alpha

    exact_claim_ok = math.isclose(exact_alpha, reference_alpha, rel_tol=0.0, abs_tol=1e-12)
    phase_observable_ok = relative_delta_error <= 1.0e-3
    strict_phase_observable_ok = relative_delta_error <= 1.0e-4

    verdict = "supported" if phase_observable_ok else "falsifie"

    return {
        "exact_alpha": exact_alpha,
        "reference_alpha": reference_alpha,
        "exact_delta_theta_rad": exact_delta_theta,
        "reference_delta_theta_rad": reference_delta_theta,
        "exact_delta_theta_deg": exact_delta_theta * 180.0 / math.pi,
        "reference_delta_theta_deg": reference_delta_theta * 180.0 / math.pi,
        "absolute_alpha_error": absolute_alpha_error,
        "relative_alpha_error": relative_alpha_error,
        "absolute_delta_error_rad": absolute_delta_error,
        "relative_delta_error": relative_delta_error,
        "exact_claim_ok": exact_claim_ok,
        "phase_observable_ok": phase_observable_ok,
        "strict_phase_observable_ok": strict_phase_observable_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_phase_deficit()
    payload = {"timestamp": timestamp, **result}

    json_path = outdir / f"alpha_phase_observable_check_{timestamp}.json"
    txt_path = outdir / f"alpha_phase_observable_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Alpha phase observable check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"exact_alpha: {result['exact_alpha']:.15f}",
        f"reference_alpha: {result['reference_alpha']:.15f}",
        f"exact_delta_theta_rad: {result['exact_delta_theta_rad']:.15f}",
        f"reference_delta_theta_rad: {result['reference_delta_theta_rad']:.15f}",
        f"exact_delta_theta_deg: {result['exact_delta_theta_deg']:.12f}",
        f"reference_delta_theta_deg: {result['reference_delta_theta_deg']:.12f}",
        f"absolute_delta_error_rad: {result['absolute_delta_error_rad']:.15f}",
        f"relative_delta_error: {result['relative_delta_error']:.6e}",
        f"exact_claim_ok: {result['exact_claim_ok']}",
        f"phase_observable_ok: {result['phase_observable_ok']}",
        f"strict_phase_observable_ok: {result['strict_phase_observable_ok']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["report_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the Delta theta = 2 pi alpha observable.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()