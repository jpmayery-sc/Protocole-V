"""Compare V16 predictions against the external reference set."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v17validation_core import compare_prediction, v17_result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = v17_result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    comparison = compare_prediction()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "V16 reste dans les bornes de reference externes",
        "case_control": "V16 vs reference minimale",
        "observable": ", ".join(row["name"] for row in comparison["rows"]),
        "expected": "ecarts faibles et signes compatibles",
        "measured": {
            "all_in_bounds": comparison["all_in_bounds"],
            "all_signs_ok": comparison["all_signs_ok"],
            "comparison_ok": comparison["comparison_ok"],
        },
        "rows": comparison["rows"],
        "comparison": comparison,
        "verdict": "supported" if comparison["comparison_ok"] else "falsified",
        "reference_label": "V17 comparison gate",
    }

    json_path = outdir / f"v17compare_check_{timestamp}.json"
    txt_path = outdir / f"v17compare_check_{timestamp}.txt"
    write_report(json_path, payload)

    txt_lines = [
        "V17 compare check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"all_in_bounds: {comparison['all_in_bounds']}",
        f"all_signs_ok: {comparison['all_signs_ok']}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare V16 predictions against the external reference set.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()