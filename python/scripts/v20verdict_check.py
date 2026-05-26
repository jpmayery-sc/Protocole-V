"""Run the V20 verdict check."""
from __future__ import annotations

import argparse
import json
import time

from v20research_core import evaluate_v20_verdict, v20_result_dir, write_report


def run_check(output_dir: str | None = None) -> dict[str, object]:
    result_dir = v20_result_dir(output_dir)
    payload = evaluate_v20_verdict()
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v20verdict_check_{timestamp}.json"
    txt_path = result_dir / f"v20verdict_check_{timestamp}.txt"
    report = {**payload, "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    result_dir.mkdir(parents=True, exist_ok=True)
    write_report(json_path, report)
    lines = [
        "V20 verdict check",
        f"timestamp: {timestamp}",
        f"verdict_global: {payload['verdict_global']}",
        f"structure_detectee: {payload['structure_detectee']}",
        f"niveau_de_confiance: {payload['niveau_de_confiance']}",
        f"zone_de_recherche_prioritaire: {payload['zone_de_recherche_prioritaire']}",
        f"geo_verdict: {payload['v20_geo']['verdict']}",
        f"torsion_verdict: {payload['v20_torsion']['verdict']}",
        f"hierarchy_verdict: {payload['v20_hierarchy']['verdict']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    report["json_path"] = str(json_path)
    report["txt_path"] = str(txt_path)
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V20 verdict check.")
    parser.add_argument("--output-dir", default=None, help="Directory for the check summary")
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()