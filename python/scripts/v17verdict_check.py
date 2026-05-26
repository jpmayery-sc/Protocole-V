"""Compute the final V17 verdict from comparison and deviation analysis."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v17validation_core import evaluate_verdict, v17_result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = v17_result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    verdict_data = evaluate_verdict()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "V16 reste compatible, marginal ou incompatible face au referentiel externe",
        "case_control": "verdict final V17",
        "observable": "comparison, deviation, verdict",
        "expected": "supported, marginal ou falsified",
        "measured": {
            "locked_names": verdict_data["comparison"]["reference"]["locked_names"],
            "frozen_names": verdict_data["comparison"]["reference"]["frozen_names"],
            "verdict": verdict_data["verdict"],
        },
        "comparison": verdict_data["comparison"],
        "deviation": verdict_data["deviation"],
        "verdict": verdict_data["verdict"],
        "reference_label": "V17 verdict gate",
    }

    json_path = outdir / f"v17verdict_check_{timestamp}.json"
    txt_path = outdir / f"v17verdict_check_{timestamp}.txt"
    write_report(json_path, payload)

    txt_lines = [
        "V17 verdict check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict_data['verdict']}",
        f"deviation_class: {verdict_data['deviation']['deviation_class']}",
        f"deviation_score: {verdict_data['deviation']['deviation_score']:.6f}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute the final V17 verdict from comparison and deviation analysis.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()