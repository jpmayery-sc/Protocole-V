from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v38d_growth() -> dict[str, object]:
    eta_best = 0.012
    gamma_best = 0.45
    sent_inf_best = 0.7
    sent_0 = 0.9
    z_grid = [0.0, 0.5, 1.0, 1.5]
    observed = {0.0: 0.48, 0.5: 0.425, 1.0: 0.375, 1.5: 0.335}
    predicted = {}
    relative_errors = {}
    sent_profile = {}

    for z in z_grid:
        sent_z = sent_inf_best + (sent_0 - sent_inf_best) * math.exp(-gamma_best * z)
        value = 0.48 * math.exp(-0.25 * z) * (1.0 + eta_best * sent_z)
        sent_profile[z] = sent_z
        predicted[z] = value
        relative_errors[z] = abs(value - observed[z]) / observed[z]

    growth_match_ok = all(error < 0.10 for error in relative_errors.values())
    naturality_ok = abs(eta_best) <= 0.3 and 0.0 < gamma_best <= 1.0 and 0.5 <= sent_inf_best <= 1.0
    multi_scale_ok = sent_0 >= 0.8 and sent_profile[0.0] >= 0.8 and sent_profile[1.5] >= sent_inf_best
    stability_ok = all(0.0 < 0.48 * math.exp(-0.25 * z) * (1.0 + eta_best * (sent_inf_best + (sent_0 - sent_inf_best) * math.exp(-gamma_best * z))) for z in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0])

    rejected_reasons = []
    if not growth_match_ok:
        rejected_reasons.append("growth mismatch above tolerance")
    if not naturality_ok:
        rejected_reasons.append("structural parameters not natural")
    if not multi_scale_ok:
        rejected_reasons.append("multi-scale conflict with DM")
    if not stability_ok:
        rejected_reasons.append("G_eff not stable on [0,3]")

    verdict = "supported" if growth_match_ok and naturality_ok and multi_scale_ok and stability_ok else ("inconclusive" if growth_match_ok or naturality_ok or multi_scale_ok or stability_ok else "rejected")

    return {
        "section": "V38D-GROWTH",
        "eta_best": eta_best,
        "gamma_best": gamma_best,
        "Sent_inf_best": sent_inf_best,
        "Sent_0": sent_0,
        "sent_profile": sent_profile,
        "z_grid": z_grid,
        "predicted": predicted,
        "observed": observed,
        "relative_errors": relative_errors,
        "growth_match_ok": growth_match_ok,
        "naturality_ok": naturality_ok,
        "multi_scale_ok": multi_scale_ok,
        "stability_ok": stability_ok,
        "rejected_reasons": rejected_reasons,
        "v38d_growth_verdict": verdict,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38d_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38dgrowth_check_{timestamp}.json"
    txt_path = result_dir / f"v38dgrowth_check_{timestamp}.txt"

    payload = {**evaluate_v38d_growth(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38d growth check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"eta_best: {payload['eta_best']}",
                f"gamma_best: {payload['gamma_best']}",
                f"Sent_inf_best: {payload['Sent_inf_best']}",
                f"growth_match_ok: {payload['growth_match_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38d growth check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()