"""Build the reduced V14 parameter vector and verify it preserves calibration."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v13calibration_core import TARGET_THETA, workspace_root
from v14reduction_core import evaluate_reduced_theta, select_reduced_names
from v14rank_check import evaluate_rank


def evaluate_reduce(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    rank_result = evaluate_rank(outdir)
    keep_names = rank_result["keep_names"]
    reduced_theta = {name: TARGET_THETA[name] for name in keep_names}
    evaluation = evaluate_reduced_theta(reduced_theta)
    reduction_ratio = len(keep_names) / len(TARGET_THETA)
    verdict = "supported" if evaluation["supported"] and reduction_ratio <= 0.75 else "falsified"

    return {
        "keep_names": keep_names,
        "freeze_names": [name for name in TARGET_THETA if name not in keep_names],
        "reduced_theta": reduced_theta,
        "evaluation": evaluation,
        "reduction_ratio": reduction_ratio,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_reduce(outdir)

    payload = {
        "timestamp": timestamp,
        "hypothesis": "un vecteur reduit peut conserver la calibration V13 tout en gelant les parametres quasi-plats",
        "case_control": "theta red vs theta MAP",
        "observable": "z_geo, z_int, z_canal, z_mod, alpha_residual, fine_delta",
        "expected": "support du point reduit, reduction ratio <= 0.75, ecart nul au MAP sur les parametres gardes",
        "measured": {
            "keep_names": result["keep_names"],
            "freeze_names": result["freeze_names"],
            "reduction_ratio": result["reduction_ratio"],
            "alpha_repaired_ok": result["evaluation"]["alpha_repaired_ok"],
            "redshift_ok": result["evaluation"]["redshift_ok"],
            "fine_ok": result["evaluation"]["fine_ok"],
            "supported": result["evaluation"]["supported"],
        },
        "reduced_theta": result["reduced_theta"],
        "full_theta": result["evaluation"]["full_theta"],
        "observables": result["evaluation"]["observables"],
        "verdict": result["verdict"],
        "reference": "V13 MAP reduction candidate",
    }

    json_path = outdir / f"v14reduce_check_{timestamp}.json"
    txt_path = outdir / f"v14reduce_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V14 reduce check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"keep_names: {', '.join(result['keep_names'])}",
        f"freeze_names: {', '.join(result['freeze_names'])}",
        f"reduction_ratio: {result['reduction_ratio']:.3f}",
        f"alpha_repaired_ok: {result['evaluation']['alpha_repaired_ok']}",
        f"redshift_ok: {result['evaluation']['redshift_ok']}",
        f"fine_ok: {result['evaluation']['fine_ok']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the reduced V14 parameter vector and verify it preserves calibration.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()