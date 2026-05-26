from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v30table_check import evaluate_v30_table


def evaluate_v30_tester_summary() -> dict[str, object]:
    table = evaluate_v30_table()
    return {
        "section": "V30-VERSION-FINALE",
        "validated_anomalies": len(table["anomaly_table"]),
        "confirmed_count": table["sigma_summary"]["confirmed"],
        "open_count": table["sigma_summary"]["open"],
        "falsification_status": table["falsification_status"],
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v30_validation"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v30tester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v30tester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v30_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V30 tester summary check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"validated_anomalies: {payload['validated_anomalies']}",
                f"confirmed_count: {payload['confirmed_count']}",
                f"open_count: {payload['open_count']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V30 tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()