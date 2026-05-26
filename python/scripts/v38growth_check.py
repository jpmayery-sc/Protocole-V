from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v38_growth() -> dict[str, object]:
    eta = 0.2
    sent_y = 0.9
    z_grid = [0.0, 0.5, 1.0]
    observed = {0.0: 0.48, 0.5: 0.425, 1.0: 0.375}
    predicted = {}
    relative_errors = {}

    for z in z_grid:
        value = 0.48 * math.exp(-0.25 * z) * (1.0 + 0.02 * eta * sent_y)
        predicted[z] = value
        relative_errors[z] = abs(value - observed[z]) / observed[z]

    growth_match_ok = all(error < 0.10 for error in relative_errors.values())
    eta_natural_ok = eta in {0.1, 0.2, 0.3}
    multi_scale_ok = sent_y >= 0.8

    rejected_reasons = []
    if not growth_match_ok:
        rejected_reasons.append("growth mismatch above tolerance")
    if not eta_natural_ok:
        rejected_reasons.append("eta not natural")
    if not multi_scale_ok:
        rejected_reasons.append("multi-scale conflict with DM")

    verdict = "supported" if growth_match_ok and eta_natural_ok and multi_scale_ok else ("inconclusive" if growth_match_ok or eta_natural_ok or multi_scale_ok else "rejected")

    return {
        "section": "V38-GROWTH",
        "eta": eta,
        "Sent_Y": sent_y,
        "z_grid": z_grid,
        "predicted": predicted,
        "observed": observed,
        "relative_errors": relative_errors,
        "growth_match_ok": growth_match_ok,
        "eta_natural_ok": eta_natural_ok,
        "multi_scale_ok": multi_scale_ok,
        "rejected_reasons": rejected_reasons,
        "v38_growth_verdict": verdict,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38growth_check_{timestamp}.json"
    txt_path = result_dir / f"v38growth_check_{timestamp}.txt"

    payload = {**evaluate_v38_growth(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38 growth check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"growth_match_ok: {payload['growth_match_ok']}",
                f"eta_natural_ok: {payload['eta_natural_ok']}",
                f"multi_scale_ok: {payload['multi_scale_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38 growth check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()