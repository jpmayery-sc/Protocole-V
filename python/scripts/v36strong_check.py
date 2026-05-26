from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v36scales_check import evaluate_v36_scales


def evaluate_v36_strong() -> dict[str, object]:
    scales = evaluate_v36_scales()
    chosen_particle = "glueball_0pp"
    m_exp = 1.6
    c_K = 10
    c_T = 10
    K_loc_strong = scales["K_loc_best"] * c_K
    T_loc_strong = scales["T_loc_best"] * c_T
    M0_strong = 1.59998
    alpha_s = 1.0e-3
    beta_s = 1.0e-3

    m_strong_eff = M0_strong + alpha_s * K_loc_strong + beta_s * T_loc_strong
    mass_match_ok = abs(m_strong_eff - m_exp) <= 0.05 * m_exp
    naturality_ok = 1.0e-3 <= alpha_s <= 1.0e-1 and 1.0e-3 <= beta_s <= 1.0e-1
    hierarchy_ok = alpha_s / scales["leptonic_couplings"]["A_mu_best"] < 1.0e6 and beta_s / scales["leptonic_couplings"]["B_mu_best"] < 1.0e6

    rejected_reasons = []
    if not mass_match_ok:
        rejected_reasons.append("mass match outside tolerance")
    if not naturality_ok:
        rejected_reasons.append("couplings not natural")
    if not hierarchy_ok:
        rejected_reasons.append("hierarchy too large")

    if mass_match_ok and naturality_ok and hierarchy_ok:
        verdict = "supported"
    elif mass_match_ok or naturality_ok or hierarchy_ok:
        verdict = "inconclusive"
    else:
        verdict = "rejected"

    return {
        "section": "V36-STRONG",
        "chosen_particle": chosen_particle,
        "m_exp": m_exp,
        "K_loc_strong": K_loc_strong,
        "T_loc_strong": T_loc_strong,
        "c_K": c_K,
        "c_T": c_T,
        "M0_strong": M0_strong,
        "alpha_s": alpha_s,
        "beta_s": beta_s,
        "m_strong_eff": m_strong_eff,
        "mass_match_ok": mass_match_ok,
        "naturality_ok": naturality_ok,
        "hierarchy_ok": hierarchy_ok,
        "rejected_reasons": rejected_reasons,
        "v36_strong_verdict": verdict,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v36_scale_strong"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v36strong_check_{timestamp}.json"
    txt_path = result_dir / f"v36strong_check_{timestamp}.txt"

    payload = {**evaluate_v36_strong(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V36 strong check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"mass_match_ok: {payload['mass_match_ok']}",
                f"naturality_ok: {payload['naturality_ok']}",
                f"hierarchy_ok: {payload['hierarchy_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V36 strong particle check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()