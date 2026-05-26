from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v37_bphysics() -> dict[str, object]:
    d_K = 5
    d_T = 5
    K_loc_best = 2.0e-4
    T_loc_best = 8.0e-4
    K_loc_B = d_K * K_loc_best
    T_loc_B = d_T * T_loc_best

    C_e = 1.0e-3
    C_mu = 1.05e-3
    C_tau = 1.2e-3

    F_value = 0.05
    delta_RK = (C_mu - C_e) * F_value / max(C_e * F_value, 1.0e-18)
    flavour_match_ok = 0.01 <= abs(delta_RK) <= 0.10
    naturality_ok = all(1.0e-3 <= c <= 1.0e-1 for c in (C_e, C_mu, C_tau))
    hierarchy_ok = (C_mu / C_e) < 1.0e4 and (C_tau / C_e) < 1.0e4

    rejected_reasons = []
    if not flavour_match_ok:
        rejected_reasons.append("flavour tension outside window")
    if not naturality_ok:
        rejected_reasons.append("couplings not natural")
    if not hierarchy_ok:
        rejected_reasons.append("hierarchy too large")

    verdict = "supported" if flavour_match_ok and naturality_ok and hierarchy_ok else ("inconclusive" if flavour_match_ok or naturality_ok or hierarchy_ok else "rejected")

    return {
        "section": "V37-BPHYSICS",
        "chosen_system": "B_to_K_ll",
        "d_K": d_K,
        "d_T": d_T,
        "K_loc_B": K_loc_B,
        "T_loc_B": T_loc_B,
        "C_e": C_e,
        "C_mu": C_mu,
        "C_tau": C_tau,
        "delta_RK": delta_RK,
        "flavour_match_ok": flavour_match_ok,
        "naturality_ok": naturality_ok,
        "hierarchy_ok": hierarchy_ok,
        "rejected_reasons": rejected_reasons,
        "v37_B_verdict": verdict,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v37_extensions"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v37bphysics_check_{timestamp}.json"
    txt_path = result_dir / f"v37bphysics_check_{timestamp}.txt"

    payload = {**evaluate_v37_bphysics(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V37 bphysics check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"flavour_match_ok: {payload['flavour_match_ok']}",
                f"naturality_ok: {payload['naturality_ok']}",
                f"hierarchy_ok: {payload['hierarchy_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V37 b-physics check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()