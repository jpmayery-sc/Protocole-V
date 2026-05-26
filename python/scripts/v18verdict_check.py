"""Compute the final V18 verdict."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v18calibration_core import baseline_payload, v18_result_dir, write_report
from v18recheck_check import run_check as run_recheck_check


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = v18_result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    recheck_report = run_recheck_check(outdir)
    baseline = baseline_payload()
    best_profile = recheck_report["best_profile"]
    improved = float(best_profile["deviation_score"]) < float(baseline["deviation_score"])

    if recheck_report["verdict"] == "degraded":
        verdict = "degraded"
    elif improved:
        verdict = "supported-improved"
    else:
        verdict = "supported-neutral"

    payload = {
        "timestamp": timestamp,
        "hypothesis": "V18 peut ameliorer la calibration externe sans casser V15/V16/V17",
        "case_control": "verdict final V18",
        "observable": "best_profile, baseline_deviation_score, best_deviation_score",
        "expected": "supported-improved, supported-neutral ou degraded",
        "measured": {
            "best_profile": best_profile["profile_name"],
            "baseline_deviation_score": baseline["deviation_score"],
            "best_deviation_score": best_profile["deviation_score"],
            "improved": improved,
        },
        "recheck": recheck_report,
        "baseline": baseline,
        "verdict": verdict,
        "reference_label": "V18 verdict gate",
    }

    json_path = outdir / f"v18verdict_check_{timestamp}.json"
    txt_path = outdir / f"v18verdict_check_{timestamp}.txt"
    write_report(json_path, payload)
    txt_lines = [
        "V18 verdict check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"best_profile: {best_profile['profile_name']}",
        f"baseline_deviation_score: {baseline['deviation_score']:.6f}",
        f"best_deviation_score: {best_profile['deviation_score']:.6f}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute the final V18 verdict.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()