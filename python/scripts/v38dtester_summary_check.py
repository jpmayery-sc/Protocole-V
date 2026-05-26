from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v38dhubble_check import run_check as run_hubble_check
from v38dlambda_check import run_check as run_lambda_check
from v38dgrowth_check import run_check as run_growth_check


def evaluate_v38d_tester_summary() -> dict[str, object]:
    hubble = run_hubble_check()
    lambda_check = run_lambda_check()
    growth = run_growth_check()

    cosmology_consistency = all(
        [
            hubble["verdict"] == "supported",
            lambda_check["verdict"] == "supported",
            growth["verdict"] == "supported",
            growth["multi_scale_ok"],
        ]
    )

    if cosmology_consistency:
        global_verdict = "supported"
    elif sum([hubble["verdict"] == "supported", lambda_check["verdict"] == "supported", growth["verdict"] == "supported"]) == 2:
        global_verdict = "partially_supported"
    else:
        global_verdict = "rejected"

    return {
        "section": "V38D-SYNTHESIS",
        "hubble_summary": {
            "v38d_hubble_verdict": hubble["verdict"],
            "hubble_match_ok": hubble["hubble_match_ok"],
        },
        "lambda_summary": {
            "v38d_lambda_verdict": lambda_check["verdict"],
            "lambda_match_ok": lambda_check["lambda_match_ok"],
        },
        "growth_summary": {
            "v38d_growth_verdict": growth["v38d_growth_verdict"],
            "growth_match_ok": growth["growth_match_ok"],
            "multi_scale_ok": growth["multi_scale_ok"],
            "stability_ok": growth["stability_ok"],
        },
        "cosmology_consistency": cosmology_consistency,
        "v38d_global_verdict": global_verdict,
        "verdict": "supported" if global_verdict == "supported" else global_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38d_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38dtester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v38dtester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v38d_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38d tester summary check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"v38d_global_verdict: {payload['v38d_global_verdict']}",
                f"cosmology_consistency: {payload['cosmology_consistency']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38d tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()