from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v38hubble_check import evaluate_v38_hubble
from v38lambda_check import evaluate_v38_lambda
from v38growth_check import evaluate_v38_growth


def evaluate_v38_tester_summary() -> dict[str, object]:
    hubble = evaluate_v38_hubble()
    lambda_check = evaluate_v38_lambda()
    growth = evaluate_v38_growth()

    cosmology_consistency = all(
        [
            hubble["v38_hubble_verdict"] == "supported",
            lambda_check["v38_lambda_verdict"] == "supported",
            growth["v38_growth_verdict"] == "supported",
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
        "section": "V38-SYNTHESIS",
        "hubble_summary": {
            "v38_hubble_verdict": hubble["v38_hubble_verdict"],
            "hubble_match_ok": hubble["hubble_match_ok"],
        },
        "lambda_summary": {
            "v38_lambda_verdict": lambda_check["v38_lambda_verdict"],
            "lambda_match_ok": lambda_check["lambda_match_ok"],
        },
        "growth_summary": {
            "v38_growth_verdict": growth["v38_growth_verdict"],
            "growth_match_ok": growth["growth_match_ok"],
        },
        "cosmology_consistency": cosmology_consistency,
        "v38_global_verdict": global_verdict,
        "verdict": "supported" if global_verdict == "supported" else global_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38tester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v38tester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v38_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38 tester summary check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"v38_global_verdict: {payload['v38_global_verdict']}",
                f"cosmology_consistency: {payload['cosmology_consistency']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38 tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()