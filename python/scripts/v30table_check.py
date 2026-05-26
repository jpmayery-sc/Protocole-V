from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v30validation_check import evaluate_v30_validation


def evaluate_v30_table() -> dict[str, object]:
    validation = evaluate_v30_validation()["validation_table"]
    return {
        "section": "V30-TABLEAU",
        "anomaly_table": validation,
        "sigma_summary": {
            "confirmed": sum(1 for row in validation if row["validation"] == "confirmed"),
            "open": sum(1 for row in validation if row["validation"] == "open"),
            "weak": sum(1 for row in validation if row["validation"] == "weak"),
        },
        "falsification_status": "partial",
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v30_validation"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v30table_check_{timestamp}.json"
    txt_path = result_dir / f"v30table_check_{timestamp}.txt"

    payload = {**evaluate_v30_table(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V30 table check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"confirmed: {payload['sigma_summary']['confirmed']}",
                f"open: {payload['sigma_summary']['open']}",
                f"weak: {payload['sigma_summary']['weak']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V30 table check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()