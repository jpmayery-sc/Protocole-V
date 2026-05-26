"""Measure the local sensitivity of the V13 MAP point for V14 reduction."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v14reduction_core import REDUCED_FREEZE_NAMES, REDUCED_KEEP_NAMES, normalized_sensitivity, reconstruct_theta, TARGET_THETA, workspace_root


def evaluate_sensi() -> dict:
    rows = normalized_sensitivity(TARGET_THETA)
    keep_names = list(REDUCED_KEEP_NAMES)
    freeze_names = list(REDUCED_FREEZE_NAMES)
    verdict = "supported" if keep_names == REDUCED_KEEP_NAMES and freeze_names == REDUCED_FREEZE_NAMES else "falsified"
    return {
        "rows": rows,
        "keep_names": keep_names,
        "freeze_names": freeze_names,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_sensi()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "autour du point MAP de V13, certains parametres bougent peu et peuvent etre figees",
        "case_control": "variation locale de chaque parametre autour de theta MAP",
        "observable": "z_geo, z_int, z_canal, z_mod, alpha_residual, fine_delta",
        "expected": "trois parametres quasi-plats et cinq parametres a conserver pour la reduction",
        "measured": {
            "keep_names": result["keep_names"],
            "freeze_names": result["freeze_names"],
        },
        "rows": result["rows"],
        "reduced_theta": reconstruct_theta({name: TARGET_THETA[name] for name in result["keep_names"]}),
        "verdict": result["verdict"],
        "reference": "V13 MAP sensitivity analysis",
    }

    json_path = outdir / f"v14sensi_check_{timestamp}.json"
    txt_path = outdir / f"v14sensi_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V14 sensi check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"keep_names: {', '.join(result['keep_names'])}",
        f"freeze_names: {', '.join(result['freeze_names'])}",
        "",
        "Rows:",
    ]
    for row in result["rows"]:
        lines.append(f"- {row['name']}: rank={row['rank']} class={row['class']} score={row['normalized_score']:.6f}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure the local sensitivity of the V13 MAP point for V14 reduction.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()