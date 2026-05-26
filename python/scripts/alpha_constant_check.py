"""Check the alpha = 1/137 claim against a reference value.

This script is intentionally small. It separates two claims:
- exact claim: alpha = 1/137 exactly,
- approximation claim: 1/137 is a usable mnemonic.
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


def evaluate_alpha() -> dict:
    exact_inverse = 137.0
    reference_inverse = REFERENCE_ALPHA_INVERSE
    absolute_error = abs(exact_inverse - reference_inverse)
    relative_error = absolute_error / reference_inverse

    exact_claim_ok = math.isclose(exact_inverse, reference_inverse, rel_tol=0.0, abs_tol=1e-12)
    mnemonic_claim_ok = relative_error <= 1.0e-3
    strict_mnemonic_ok = relative_error <= 1.0e-4

    if exact_claim_ok:
        verdict = "supported"
    else:
        verdict = "falsifie"

    return {
        "exact_inverse": exact_inverse,
        "reference_inverse": reference_inverse,
        "absolute_error": absolute_error,
        "relative_error": relative_error,
        "exact_claim_ok": exact_claim_ok,
        "mnemonic_claim_ok": mnemonic_claim_ok,
        "strict_mnemonic_ok": strict_mnemonic_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_alpha()

    payload = {"timestamp": timestamp, **result}

    json_path = outdir / f"alpha_constant_check_{timestamp}.json"
    txt_path = outdir / f"alpha_constant_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Alpha constant check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"exact_inverse: {result['exact_inverse']:.12f}",
        f"reference_inverse: {result['reference_inverse']:.12f}",
        f"absolute_error: {result['absolute_error']:.12f}",
        f"relative_error: {result['relative_error']:.6e}",
        f"exact_claim_ok: {result['exact_claim_ok']}",
        f"mnemonic_claim_ok: {result['mnemonic_claim_ok']}",
        f"strict_mnemonic_ok: {result['strict_mnemonic_ok']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["report_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether alpha = 1/137 is exact or only mnemonic.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()