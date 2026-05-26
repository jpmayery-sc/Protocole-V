"""Lock the V15 reduced model and verify the final vector stays supported."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v15consolidation_core import FINAL_FROZEN_NAMES, FINAL_LOCKED_NAMES, evaluate_locked_theta, final_locked_theta, workspace_root


def evaluate_lock() -> dict:
    theta = final_locked_theta()
    evaluation = evaluate_locked_theta(theta)
    verdict = "supported" if evaluation["supported"] and evaluation["locked_names"] == FINAL_LOCKED_NAMES else "falsified"
    return {
        "reduced_theta": theta,
        "evaluation": evaluation,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_lock()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "le vecteur final peut etre fige sans perdre la compatibilite V11-V14",
        "case_control": "vecteur reduit verrouille",
        "observable": "theta final, redshifts, alpha_residual, fine_delta",
        "expected": "cinq parametres gardes, trois parametres figes, support conserve",
        "measured": {
            "locked_names": result["evaluation"]["locked_names"],
            "frozen_names": result["evaluation"]["frozen_names"],
            "supported": result["evaluation"]["supported"],
            "alpha_repaired_ok": result["evaluation"]["alpha_repaired_ok"],
            "redshift_ok": result["evaluation"]["redshift_ok"],
            "fine_ok": result["evaluation"]["fine_ok"],
        },
        "reduced_theta": result["reduced_theta"],
        "full_theta": result["evaluation"]["full_theta"],
        "observables": result["evaluation"]["observables"],
        "verdict": result["verdict"],
        "reference": "V15 lock consolidation",
    }

    json_path = outdir / f"v15lock_check_{timestamp}.json"
    txt_path = outdir / f"v15lock_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V15 lock check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"locked_names: {', '.join(result['evaluation']['locked_names'])}",
        f"frozen_names: {', '.join(result['evaluation']['frozen_names'])}",
        f"supported: {result['evaluation']['supported']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Lock the V15 reduced model and verify the final vector stays supported.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()