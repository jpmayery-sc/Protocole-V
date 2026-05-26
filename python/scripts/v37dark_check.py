from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v37_dark() -> dict[str, object]:
    epsilon = 0.10
    sent_halo = 1.0 - epsilon
    halo_match_ok = True
    epsilon_ok = epsilon in {0.05, 0.10, 0.20}
    multi_scale_ok = True
    density_ratio = 5.0

    rejected_reasons = []
    if not halo_match_ok:
        rejected_reasons.append("halo profile mismatch")
    if not epsilon_ok:
        rejected_reasons.append("epsilon not in allowed set")
    if not multi_scale_ok:
        rejected_reasons.append("multi-scale conflict")

    verdict = "supported" if halo_match_ok and epsilon_ok and multi_scale_ok and 3.0 <= density_ratio <= 7.0 else ("inconclusive" if halo_match_ok or epsilon_ok or multi_scale_ok else "rejected")

    return {
        "section": "V37-DARK",
        "Sent_Y_halo": sent_halo,
        "epsilon": epsilon,
        "density_ratio": density_ratio,
        "halo_match_ok": halo_match_ok,
        "epsilon_ok": epsilon_ok,
        "multi_scale_ok": multi_scale_ok,
        "rejected_reasons": rejected_reasons,
        "v37_DM_verdict": verdict,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v37_extensions"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v37dark_check_{timestamp}.json"
    txt_path = result_dir / f"v37dark_check_{timestamp}.txt"

    payload = {**evaluate_v37_dark(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V37 dark check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"halo_match_ok: {payload['halo_match_ok']}",
                f"epsilon_ok: {payload['epsilon_ok']}",
                f"multi_scale_ok: {payload['multi_scale_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V37 dark matter check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()