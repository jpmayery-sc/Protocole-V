"""Measure the structural robustness of the V15 locked model."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v15consolidation_core import FINAL_FROZEN_NAMES, FINAL_LOCKED_NAMES, evaluate_robustness_case, final_locked_theta, workspace_root


def evaluate_robustness() -> dict:
    theta = final_locked_theta()
    rows = [evaluate_robustness_case(theta, name) for name in FINAL_LOCKED_NAMES]
    verdict = "supported" if all(row["supported"] for row in rows) else "falsified"
    return {
        "reduced_theta": theta,
        "rows": rows,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_robustness()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la structure reduite preserve la coherence des redshifts, du champ alpha et du canal kappa",
        "case_control": "variations signees autour du vecteur reduit verrouille",
        "observable": "z_geo, z_int, z_canal, z_mod, alpha_residual, fine_delta",
        "expected": "les tendances attendues restent monotones et coherentes",
        "measured": {
            "locked_names": FINAL_LOCKED_NAMES,
            "frozen_names": FINAL_FROZEN_NAMES,
            "supported_rows": sum(1 for row in result["rows"] if row["supported"]),
            "total_rows": len(result["rows"]),
        },
        "rows": result["rows"],
        "reduced_theta": result["reduced_theta"],
        "verdict": result["verdict"],
        "reference": "V15 robustness consolidation",
    }

    json_path = outdir / f"v15robustness_check_{timestamp}.json"
    txt_path = outdir / f"v15robustness_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V15 robustness check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"locked_names: {', '.join(FINAL_LOCKED_NAMES)}",
        f"frozen_names: {', '.join(FINAL_FROZEN_NAMES)}",
        f"supported_rows: {payload['measured']['supported_rows']}/{payload['measured']['total_rows']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure the structural robustness of the V15 locked model.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()