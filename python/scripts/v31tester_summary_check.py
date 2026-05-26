from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v31synthesis_check import evaluate_v31_synthesis


def evaluate_v31_tester_summary() -> dict[str, object]:
    synthesis = evaluate_v31_synthesis()
    return {
        "section": "V31-VERSION-FINALE",
        "validated_families": len(synthesis["family_partition"]),
        "validated_anomalies": len(synthesis["geometric_anomaly_map"]),
        "kty_consistency": synthesis["kty_consistency"],
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v31_geometric_interpretation"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v31tester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v31tester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v31_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    lines = [
        "V31 tester summary check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"validated_families: {payload['validated_families']}",
        f"validated_anomalies: {payload['validated_anomalies']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V31 tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()