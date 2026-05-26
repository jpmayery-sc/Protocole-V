"""Run the V21 recovery check."""
from __future__ import annotations

import argparse
import json
import time

from v21borderline_core import evaluate_recovery, v21_result_dir, write_report


def run_check(output_dir: str | None = None) -> dict[str, object]:
    result_dir = v21_result_dir(output_dir)
    payload = evaluate_recovery()
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v21recovery_check_{timestamp}.json"
    txt_path = result_dir / f"v21recovery_check_{timestamp}.txt"
    report = {**payload, "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    result_dir.mkdir(parents=True, exist_ok=True)
    write_report(json_path, report)
    lines = [
        "V21 recovery check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"recovery_margin: {payload['recovery_margin']}",
        f"recovery_depth: {payload['recovery_depth']}",
        f"resolution_score: {payload['resolution_score']}",
        f"supported_chain_length: {payload['supported_chain_length']}",
        f"bottleneck_flag: {payload['bottleneck_flag']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report["json_path"] = str(json_path)
    report["txt_path"] = str(txt_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V21 recovery check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the check summary")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()