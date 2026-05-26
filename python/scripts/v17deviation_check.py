"""Analyze deviations between V16 predictions and the external reference set."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v17validation_core import analyze_deviation, v17_result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = v17_result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    deviation = analyze_deviation()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "les ecarts V16/reference restent faibles",
        "case_control": "reference minimale",
        "observable": "deviation_score, deviation_class, deviation_vector",
        "expected": "deviation_supported ou marginal",
        "measured": {
            "deviation_score": deviation["deviation_score"],
            "deviation_class": deviation["deviation_class"],
            "monotone_ok": deviation["monotone_ok"],
        },
        "deviation_vector": deviation["deviation_vector"],
        "comparison": deviation["comparison"],
        "verdict": deviation["deviation_class"],
        "reference_label": "V17 deviation gate",
    }

    json_path = outdir / f"v17deviation_check_{timestamp}.json"
    txt_path = outdir / f"v17deviation_check_{timestamp}.txt"
    write_report(json_path, payload)

    txt_lines = [
        "V17 deviation check",
        f"timestamp: {timestamp}",
        f"deviation_class: {deviation['deviation_class']}",
        f"deviation_score: {deviation['deviation_score']:.6f}",
        f"monotone_ok: {deviation['monotone_ok']}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze deviations between V16 predictions and the external reference set.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()