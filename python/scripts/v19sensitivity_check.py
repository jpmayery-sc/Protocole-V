"""Run the V19 sensitivity check."""
from __future__ import annotations

import argparse
import json
import time

from v19metacalibration_core import evaluate_sensitivity, v19_result_dir, write_report


def run_check(output_dir: str | None = None) -> dict[str, object]:
    result_dir = v19_result_dir(output_dir)
    payload = evaluate_sensitivity()
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v19sensitivity_check_{timestamp}.json"
    txt_path = result_dir / f"v19sensitivity_check_{timestamp}.txt"
    report = {**payload, "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    result_dir.mkdir(parents=True, exist_ok=True)
    write_report(json_path, report)
    lines = [
        "V19 sensitivity check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"top2_stable: {payload['top2_stable']}",
        f"dominant_gap: {payload['dominant_gap']}",
        f"median_abs_derivative: {payload['median_abs_derivative']}",
        "",
        "Ranking:",
    ]
    for row in payload["ranking"]:
        lines.append(f"- {row['parameter']}: derivative={row['derivative']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report["json_path"] = str(json_path)
    report["txt_path"] = str(txt_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V19 sensitivity check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the check summary")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()