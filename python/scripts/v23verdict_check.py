"""Run the V23 verdict check."""
from __future__ import annotations

import argparse
import json
import time

from v23theorysynthesis_core import evaluate_v23_verdict, v23_result_dir, write_report


def run_check(output_dir: str | None = None) -> dict[str, object]:
    result_dir = v23_result_dir(output_dir)
    payload = evaluate_v23_verdict()
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v23verdict_check_{timestamp}.json"
    txt_path = result_dir / f"v23verdict_check_{timestamp}.txt"
    report = {**payload, "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    result_dir.mkdir(parents=True, exist_ok=True)
    write_report(json_path, report)
    txt_path.write_text(
        "\n".join(
            [
                "V23 verdict check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"v23verdict: {payload['v23verdict']}",
                f"confidence_level: {payload['confidence_level']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    report["json_path"] = str(json_path)
    report["txt_path"] = str(txt_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V23 verdict check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the check summary")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()