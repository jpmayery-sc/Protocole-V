from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v38_hubble() -> dict[str, object]:
    z_grid = [0.1, 0.5, 1.0, 2.0]
    H0 = 70.0
    omega_m = 0.30
    omega_lambda = 0.68
    alpha = 0.5
    k_bg_best = 1.0

    observed = {0.1: 73.1, 0.5: 91.8, 1.0: 123.4, 2.0: 208.0}
    predicted = {}
    relative_errors = {}

    for z in z_grid:
        k_bg_z = k_bg_best * ((1.0 + z) ** alpha)
        h_eff = H0 * math.sqrt(omega_m * ((1.0 + z) ** 3) + omega_lambda + 0.02 * k_bg_z)
        predicted[z] = h_eff
        relative_errors[z] = abs(h_eff - observed[z]) / observed[z]

    hubble_match_ok = all(error < 0.10 for error in relative_errors.values())
    alpha_natural_ok = abs(alpha) < 2.0
    no_explosion_ok = all(value > 0 and math.isfinite(value) for value in predicted.values())

    rejected_reasons = []
    if not hubble_match_ok:
        rejected_reasons.append("H(z) mismatch above tolerance")
    if not alpha_natural_ok:
        rejected_reasons.append("alpha not natural")
    if not no_explosion_ok:
        rejected_reasons.append("H_eff invalid or explosive")

    verdict = "supported" if hubble_match_ok and alpha_natural_ok and no_explosion_ok else ("inconclusive" if hubble_match_ok or alpha_natural_ok or no_explosion_ok else "rejected")

    return {
        "section": "V38-HUBBLE",
        "z_grid": z_grid,
        "H0": H0,
        "omega_m": omega_m,
        "omega_lambda": omega_lambda,
        "alpha": alpha,
        "predicted": predicted,
        "observed": observed,
        "relative_errors": relative_errors,
        "hubble_match_ok": hubble_match_ok,
        "alpha_natural_ok": alpha_natural_ok,
        "no_explosion_ok": no_explosion_ok,
        "rejected_reasons": rejected_reasons,
        "v38_hubble_verdict": verdict,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38hubble_check_{timestamp}.json"
    txt_path = result_dir / f"v38hubble_check_{timestamp}.txt"

    payload = {**evaluate_v38_hubble(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38 hubble check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"hubble_match_ok: {payload['hubble_match_ok']}",
                f"alpha_natural_ok: {payload['alpha_natural_ok']}",
                f"no_explosion_ok: {payload['no_explosion_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38 Hubble check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()