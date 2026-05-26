"""Re-run V16 and V17 with the best V18 calibration profile."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v18calibration_core import baseline_payload, build_profile_payload, select_best_profile, v18_result_dir, write_report
from v18calibrate_check import run_check as run_calibrate_check


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = v18_result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    calibrate_report = run_calibrate_check(outdir)
    baseline = calibrate_report["baseline"]
    best_profile = select_best_profile(calibrate_report["profiles"])

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la meilleure calibration V18 conserve V16/V17 et reduit le delta",
        "case_control": "best profile V18",
        "observable": "internal_ok, external_ok, comparison_ok, deviation_score",
        "expected": "scores en baisse et support conserve",
        "measured": {
            "best_profile": best_profile["profile_name"],
            "baseline_deviation_score": baseline["deviation_score"],
            "best_deviation_score": best_profile["deviation_score"],
            "improved": float(best_profile["deviation_score"]) < float(baseline["deviation_score"]),
            "internal_ok": best_profile["internal_ok"],
            "external_ok": best_profile["external_ok"],
            "comparison_ok": best_profile["comparison_ok"],
        },
        "best_profile": best_profile,
        "baseline": baseline,
        "verdict": "supported" if best_profile["supported"] else "degraded",
        "reference_label": "V18 recheck gate",
    }

    json_path = outdir / f"v18recheck_check_{timestamp}.json"
    txt_path = outdir / f"v18recheck_check_{timestamp}.txt"
    write_report(json_path, payload)
    txt_lines = [
        "V18 recheck check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"best_profile: {best_profile['profile_name']}",
        f"baseline_deviation_score: {baseline['deviation_score']:.6f}",
        f"best_deviation_score: {best_profile['deviation_score']:.6f}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Re-run V16 and V17 with the best V18 calibration profile.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()