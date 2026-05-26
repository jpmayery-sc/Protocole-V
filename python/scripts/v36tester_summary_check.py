from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v36scales_check import evaluate_v36_scales
from v36strong_check import evaluate_v36_strong


def evaluate_v36_tester_summary() -> dict[str, object]:
    scales = evaluate_v36_scales()
    strong = evaluate_v36_strong()
    multi_scale_consistency = bool(
        scales["K_loc_best"] > 0
        and scales["T_loc_best"] > 0
        and strong["mass_match_ok"]
        and strong["naturality_ok"]
        and strong["hierarchy_ok"]
    )

    if scales["verdict"] == "supported" and strong["v36_strong_verdict"] == "supported":
        global_verdict = "supported"
    elif scales["verdict"] == "rejected" and strong["v36_strong_verdict"] == "rejected":
        global_verdict = "rejected"
    else:
        global_verdict = "partially_supported"

    return {
        "section": "V36-SYNTHESIS",
        "scales_summary": {
            "K_loc_best": scales["K_loc_best"],
            "T_loc_best": scales["T_loc_best"],
            "K_bg_best": scales["K_bg_best"],
            "K_loc_strong": strong["K_loc_strong"],
            "T_loc_strong": strong["T_loc_strong"],
        },
        "couplings_summary": {
            "A_mu_best": scales["leptonic_couplings"]["A_mu_best"],
            "B_mu_best": scales["leptonic_couplings"]["B_mu_best"],
            "lambda_2_best": scales["neutrino_couplings"]["lambda_2_best"],
            "lambda_3_best": scales["neutrino_couplings"]["lambda_3_best"],
            "alpha_s": strong["alpha_s"],
            "beta_s": strong["beta_s"],
        },
        "multi_scale_consistency": multi_scale_consistency,
        "v36_global_verdict": global_verdict,
        "verdict": "supported" if global_verdict == "supported" else global_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v36_scale_strong"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v36tester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v36tester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v36_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V36 tester summary check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"v36_global_verdict: {payload['v36_global_verdict']}",
                f"multi_scale_consistency: {payload['multi_scale_consistency']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V36 tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()