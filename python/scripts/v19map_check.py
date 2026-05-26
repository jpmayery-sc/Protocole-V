"""Run the V19 map check."""
from __future__ import annotations

import argparse
import json
import time

from v19metacalibration_core import evaluate_map, v19_result_dir, write_report


def run_check(output_dir: str | None = None) -> dict[str, object]:
    result_dir = v19_result_dir(output_dir)
    payload = evaluate_map()
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v19map_check_{timestamp}.json"
    txt_path = result_dir / f"v19map_check_{timestamp}.txt"
    report = {**payload, "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    result_dir.mkdir(parents=True, exist_ok=True)
    write_report(json_path, report)
    lines = [
        "V19 map check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"supported_count: {payload['supported_count']}/{payload['total']}",
        f"baseline_deviation_score: {payload['baseline_deviation_score']}",
        f"supported_ratio: {payload['supported_ratio']}",
        "",
        "Axes:",
    ]
    for axis in payload["axes"]:
        lines.append(f"- {axis['axis']}: {axis['verdict']} ({axis['stability_state']})")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report["json_path"] = str(json_path)
    report["txt_path"] = str(txt_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V19 map check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the check summary")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()