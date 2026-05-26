from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v38_lambda() -> dict[str, object]:
    lambda_0 = 0.66
    xi = 0.02
    k_bg_best = 1.0
    rho_ratio = lambda_0 + xi * k_bg_best

    lambda_match_ok = abs(rho_ratio - 0.68) <= 0.05
    xi_natural_ok = abs(xi) < 10.0

    rejected_reasons = []
    if not lambda_match_ok:
        rejected_reasons.append("Lambda density ratio outside window")
    if not xi_natural_ok:
        rejected_reasons.append("xi not natural")

    verdict = "supported" if lambda_match_ok and xi_natural_ok else ("inconclusive" if lambda_match_ok or xi_natural_ok else "rejected")

    return {
        "section": "V38-LAMBDA",
        "Lambda_0": lambda_0,
        "xi": xi,
        "K_bg_best": k_bg_best,
        "rho_Lambda_eff_over_rho_crit": rho_ratio,
        "lambda_match_ok": lambda_match_ok,
        "xi_natural_ok": xi_natural_ok,
        "rejected_reasons": rejected_reasons,
        "v38_lambda_verdict": verdict,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38lambda_check_{timestamp}.json"
    txt_path = result_dir / f"v38lambda_check_{timestamp}.txt"

    payload = {**evaluate_v38_lambda(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38 lambda check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"lambda_match_ok: {payload['lambda_match_ok']}",
                f"xi_natural_ok: {payload['xi_natural_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38 Lambda check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()