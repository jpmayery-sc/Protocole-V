from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v38chubble_check import evaluate_v38c_hubble
from v38clambda_check import evaluate_v38c_lambda
from v38cgrowth_check import evaluate_v38c_growth


def evaluate_v38c_tester_summary() -> dict[str, object]:
    hubble = evaluate_v38c_hubble()
    lambda_check = evaluate_v38c_lambda()
    growth = evaluate_v38c_growth()

    cosmology_consistency = all(
        [
            hubble["verdict"] == "supported",
            lambda_check["verdict"] == "supported",
            growth["verdict"] == "supported",
            growth["stability_ok"],
        ]
    )

    supported_count = sum([
        hubble["verdict"] == "supported",
        lambda_check["verdict"] == "supported",
        growth["verdict"] == "supported",
        cosmology_consistency,
    ])

    if cosmology_consistency:
        global_verdict = "supported"
    elif supported_count >= 3:
        global_verdict = "partially_supported"
    else:
        global_verdict = "rejected"

    return {
        "section": "V38c-SYNTHESIS",
        "hubble_summary": {"verdict": hubble["verdict"]},
        "lambda_summary": {"verdict": lambda_check["verdict"]},
        "growth_summary": {
            "v38c_growth_verdict": growth["v38c_growth_verdict"],
            "growth_match_ok": growth["growth_match_ok"],
            "stability_ok": growth["stability_ok"],
        },
        "cosmology_consistency": cosmology_consistency,
        "v38c_global_verdict": global_verdict,
        "verdict": "supported" if global_verdict == "supported" else global_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38c_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38ctester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v38ctester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v38c_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38c tester summary check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"v38c_global_verdict: {payload['v38c_global_verdict']}",
                f"cosmology_consistency: {payload['cosmology_consistency']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38c tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()