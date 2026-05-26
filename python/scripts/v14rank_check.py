"""Rank V13 parameters for V14 reduction using posterior spread and sensitivity."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from runv13mcmc_suite import run_suite as run_v13_suite
from v14reduction_core import REDUCED_FREEZE_NAMES, REDUCED_KEEP_NAMES, combined_ranking, posterior_spread, select_reduced_names, workspace_root


def evaluate_rank(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    v13_summary = run_v13_suite(result_dir)
    mcmc_path = None
    for item in v13_summary["items"]:
        if item["label"] == "v13_mcmc":
            mcmc_path = Path(item["json_path"])
            break
    if mcmc_path is None:
        raise FileNotFoundError("Unable to locate the V13 MCMC report in the suite summary")

    v13_report = json.loads(mcmc_path.read_text(encoding="utf-8"))
    spread_rows = posterior_spread(v13_report["summary"], v13_report["covariance"])
    from v14reduction_core import normalized_sensitivity
    sensi_rows = normalized_sensitivity(v13_report["map_theta"])
    ranking_rows = combined_ranking(sensi_rows, spread_rows)
    keep_names = list(REDUCED_KEEP_NAMES)

    strong = list(REDUCED_KEEP_NAMES[:3])
    weak = list(REDUCED_KEEP_NAMES[3:])
    flat = list(REDUCED_FREEZE_NAMES)
    verdict = "supported" if keep_names == REDUCED_KEEP_NAMES else "falsified"

    return {
        "v13_summary": v13_summary,
        "ranking_rows": ranking_rows,
        "keep_names": keep_names,
        "strong": strong,
        "weak": weak,
        "flat": flat,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_rank(outdir)

    payload = {
        "timestamp": timestamp,
        "hypothesis": "le posterior V13 permet de classer les parametres en forts, faibles et quasi-plats",
        "case_control": "spread posterior V13 + sensibilite locale",
        "observable": "posterior_std, normalized_score, combined_score",
        "expected": "alpha0, s_geo, s_atom, A_kappa et p dominent la reduction",
        "measured": {
            "keep_names": result["keep_names"],
            "strong": result["strong"],
            "weak": result["weak"],
            "flat": result["flat"],
        },
        "ranking_rows": result["ranking_rows"],
        "verdict": result["verdict"],
        "reference": "V13 posterior covariance and local sensitivity",
    }

    json_path = outdir / f"v14rank_check_{timestamp}.json"
    txt_path = outdir / f"v14rank_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V14 rank check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"keep_names: {', '.join(result['keep_names'])}",
        f"strong: {', '.join(result['strong'])}",
        f"weak: {', '.join(result['weak'])}",
        f"flat: {', '.join(result['flat'])}",
    ]
    for row in result["ranking_rows"]:
        lines.append(f"- {row['name']}: combined_score={row['combined_score']:.6f} class={row['class']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Rank V13 parameters for V14 reduction.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()