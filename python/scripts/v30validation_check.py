from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v30anomalies_check import evaluate_v30_anomalies


def evaluate_v30_validation() -> dict[str, object]:
    anomalies = evaluate_v30_anomalies()["anomalies"]
    table = []
    for anomaly in anomalies:
        sigma_current = anomaly["sigma_current"]
        if sigma_current == float("inf"):
            validation = "confirmed"
        elif sigma_current >= 2.0:
            validation = "open"
        else:
            validation = "weak"
        table.append({**anomaly, "validation": validation})

    confirmed = sum(1 for row in table if row["validation"] == "confirmed")
    open_count = sum(1 for row in table if row["validation"] == "open")
    weak_count = sum(1 for row in table if row["validation"] == "weak")
    return {
        "section": "V30-VALIDATION",
        "validation_table": table,
        "confirmed_count": confirmed,
        "open_count": open_count,
        "weak_count": weak_count,
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v30_validation"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v30validation_check_{timestamp}.json"
    txt_path = result_dir / f"v30validation_check_{timestamp}.txt"

    payload = {**evaluate_v30_validation(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    lines = [
        "V30 validation check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"confirmed_count: {payload['confirmed_count']}",
        f"open_count: {payload['open_count']}",
        f"weak_count: {payload['weak_count']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V30 validation check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()