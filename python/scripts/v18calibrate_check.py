"""Run the three V18 calibration profiles under controlled constraints."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v18calibration_core import CALIBRATION_PROFILES, PROFILE_ORDER, apply_profile, baseline_payload, build_profile_payload, select_best_profile, v18_result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = v18_result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    baseline = baseline_payload()
    base_theta = baseline["theta_v18"]

    profiles = []
    for profile_name in PROFILE_ORDER:
        theta_v18 = apply_profile(base_theta, profile_name)
        profiles.append(build_profile_payload(profile_name, theta_v18))

    best_profile = select_best_profile(profiles)
    improved = float(best_profile["deviation_score"]) < float(baseline["deviation_score"])
    neutral = float(best_profile["deviation_score"]) == float(baseline["deviation_score"])

    payload = {
        "timestamp": timestamp,
        "hypothesis": "trois calibrations fines peuvent reduire les ecarts sans casser la stabilite V15",
        "case_control": "calibration douce, standard, agressive",
        "observable": "deviation_score, deviation_class, internal_ok, external_ok, comparison_ok",
        "expected": "au moins une calibration ameliore le score sans degradation",
        "measured": {
            "profile_count": len(profiles),
            "supported_profiles": sum(1 for profile in profiles if profile["supported"]),
            "best_profile": best_profile["profile_name"],
            "best_deviation_score": best_profile["deviation_score"],
            "baseline_deviation_score": baseline["deviation_score"],
            "improved": improved,
            "neutral": neutral,
        },
        "baseline": baseline,
        "profiles": profiles,
        "verdict": "supported-improved" if improved else ("supported-neutral" if neutral else "degraded"),
        "reference_label": "V18 calibration gate",
    }

    json_path = outdir / f"v18calibrate_check_{timestamp}.json"
    txt_path = outdir / f"v18calibrate_check_{timestamp}.txt"
    write_report(json_path, payload)
    txt_lines = [
        "V18 calibrate check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"best_profile: {best_profile['profile_name']}",
        f"baseline_deviation_score: {baseline['deviation_score']:.6f}",
        f"best_deviation_score: {best_profile['deviation_score']:.6f}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the three V18 calibration profiles under controlled constraints.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()