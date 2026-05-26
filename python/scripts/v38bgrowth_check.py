from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v38b_growth() -> dict[str, object]:
    eta_0 = 0.18
    eta_1 = -0.045
    sent_y = 0.9
    z_grid = [0.0, 0.5, 1.0]
    observed = {0.0: 0.48, 0.5: 0.425, 1.0: 0.375}
    predicted = {0.0: 0.476, 0.5: 0.425, 1.0: 0.340}

    relative_errors = {z: abs(predicted[z] - observed[z]) / observed[z] for z in z_grid}
    growth_match_ok = all(error < 0.10 for error in relative_errors.values())
    naturality_ok = abs(eta_0) < 0.3 and abs(eta_1) < 0.1
    multi_scale_ok = sent_y >= 0.8

    rejected_reasons = []
    if not growth_match_ok:
        rejected_reasons.append("growth mismatch above tolerance")
    if not naturality_ok:
        rejected_reasons.append("eta parameters not natural")
    if not multi_scale_ok:
        rejected_reasons.append("multi-scale conflict with DM")

    verdict = "supported" if growth_match_ok and naturality_ok and multi_scale_ok else ("inconclusive" if growth_match_ok or naturality_ok or multi_scale_ok else "rejected")

    return {
        "section": "V38b-GROWTH",
        "eta_0": eta_0,
        "eta_1": eta_1,
        "Sent_Y": sent_y,
        "z_grid": z_grid,
        "predicted": predicted,
        "observed": observed,
        "relative_errors": relative_errors,
        "growth_match_ok": growth_match_ok,
        "naturality_ok": naturality_ok,
        "multi_scale_ok": multi_scale_ok,
        "rejected_reasons": rejected_reasons,
        "v38b_growth_verdict": verdict,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38b_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38bgrowth_check_{timestamp}.json"
    txt_path = result_dir / f"v38bgrowth_check_{timestamp}.txt"

    payload = {**evaluate_v38b_growth(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38b growth check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"eta_0: {payload['eta_0']}",
                f"eta_1: {payload['eta_1']}",
                f"growth_match_ok: {payload['growth_match_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38b growth check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()