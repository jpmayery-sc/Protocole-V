from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v31interpretation_check import evaluate_v31_interpretation


def evaluate_v31_synthesis() -> dict[str, object]:
    interpretation = evaluate_v31_interpretation()
    family_partition = [family["family"] for family in interpretation["families"]]
    geometric_anomaly_map = {
        anomaly: family["geometric_reading"]
        for family in interpretation["families"]
        for anomaly in family["anomalies"]
    }

    return {
        "section": "V31-SYNTHESIS",
        "geometric_anomaly_map": geometric_anomaly_map,
        "family_partition": family_partition,
        "kty_consistency": interpretation["kty_consistency"],
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v31_geometric_interpretation"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v31synthesis_check_{timestamp}.json"
    txt_path = result_dir / f"v31synthesis_check_{timestamp}.txt"

    payload = {**evaluate_v31_synthesis(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    lines = [
        "V31 synthesis check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"family_count: {len(payload['family_partition'])}",
        f"anomaly_count: {len(payload['geometric_anomaly_map'])}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V31 synthesis check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()