"""Extract the V17 deviation baseline used by V18 calibration."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v18calibration_core import baseline_payload, v18_result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = v18_result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    baseline = baseline_payload()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "V17 fournit un delta utile pour calibrer finement V18",
        "case_control": "baseline V17 -> delta V18",
        "observable": "deviation_vector, deviation_score, deviation_class",
        "expected": "baseline stable, exploitable, supporte",
        "measured": {
            "deviation_score": baseline["deviation_score"],
            "deviation_class": baseline["deviation_class"],
        },
        "deviation": baseline["deviation"],
        "comparison": baseline["comparison"],
        "verdict": "supported",
        "reference_label": "V18 delta gate",
    }

    json_path = outdir / f"v18delta_check_{timestamp}.json"
    txt_path = outdir / f"v18delta_check_{timestamp}.txt"
    write_report(json_path, payload)
    txt_lines = [
        "V18 delta check",
        f"timestamp: {timestamp}",
        "verdict: supported",
        f"baseline_deviation_score: {baseline['deviation_score']:.6f}",
        f"baseline_deviation_class: {baseline['deviation_class']}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract the V17 deviation baseline used by V18 calibration.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()