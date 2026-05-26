from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v37bphysics_check import evaluate_v37_bphysics
from v37dark_check import evaluate_v37_dark


def evaluate_v37_tester_summary() -> dict[str, object]:
    bphysics = evaluate_v37_bphysics()
    dark = evaluate_v37_dark()

    if bphysics["v37_B_verdict"] == "supported" and dark["v37_DM_verdict"] == "supported":
        global_verdict = "supported"
    elif bphysics["v37_B_verdict"] == "rejected" and dark["v37_DM_verdict"] == "rejected":
        global_verdict = "rejected"
    else:
        global_verdict = "partially_supported"

    return {
        "section": "V37-SYNTHESIS",
        "flavour_summary": {
            "v37_B_verdict": bphysics["v37_B_verdict"],
            "delta_RK": bphysics["delta_RK"],
        },
        "dark_summary": {
            "v37_DM_verdict": dark["v37_DM_verdict"],
            "Sent_Y_halo": dark["Sent_Y_halo"],
        },
        "multi_sector_consistency": bphysics["v37_B_verdict"] == "supported" and dark["v37_DM_verdict"] == "supported",
        "v37_global_verdict": global_verdict,
        "verdict": "supported" if global_verdict == "supported" else global_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v37_extensions"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v37tester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v37tester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v37_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V37 tester summary check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"v37_global_verdict: {payload['v37_global_verdict']}",
                f"multi_sector_consistency: {payload['multi_sector_consistency']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V37 tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()