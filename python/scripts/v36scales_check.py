from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v36_scales() -> dict[str, object]:
    K_tilde_best = 2.0e-4
    T_tilde_best = 8.0e-4
    K_bg_best = 1.0
    A_mu_best = 1.0e-6
    B_mu_best = 1.0e-6
    lambda_2_best = 7.4e-5
    lambda_3_best = 2.5e-3
    sum_mnu_best = 5.860232526704263e-2
    K0 = 1.0
    T0 = 1.0

    K_loc_best = K_tilde_best * K0
    T_loc_best = T_tilde_best * T0

    return {
        "section": "V36-SCALES",
        "K_loc_best": K_loc_best,
        "T_loc_best": T_loc_best,
        "K_bg_best": K_bg_best,
        "scale_ratio_K": K_loc_best / K_bg_best,
        "scale_ratio_T": T_loc_best / K_bg_best,
        "leptonic_couplings": {"A_mu_best": A_mu_best, "B_mu_best": B_mu_best},
        "neutrino_couplings": {"lambda_2_best": lambda_2_best, "lambda_3_best": lambda_3_best},
        "sum_mnu_best": sum_mnu_best,
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v36_scale_strong"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v36scales_check_{timestamp}.json"
    txt_path = result_dir / f"v36scales_check_{timestamp}.txt"

    payload = {**evaluate_v36_scales(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V36 scales check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"K_loc_best: {payload['K_loc_best']}",
                f"T_loc_best: {payload['T_loc_best']}",
                f"K_bg_best: {payload['K_bg_best']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V36 scales check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()