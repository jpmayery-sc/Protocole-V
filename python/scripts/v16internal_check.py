"""Compute internal V16 predictions from the locked V15 nucleus."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v16prediction_core import evaluate_consistency, result_dir, write_report
from v15consolidation_core import FINAL_FROZEN_NAMES, FINAL_LOCKED_NAMES


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    evaluation = evaluate_consistency()
    internal = evaluation["internal"]

    payload = {
        "timestamp": timestamp,
        "hypothesis": "le noyau V15 produit des prédictions internes stables et coherentes",
        "case_control": "vecteur verrouille V15",
        "observable": ", ".join(["z_geo", "z_int", "z_canal", "z_mod", "fine_delta", "alpha_residual"]),
        "expected": "sorties internes positives, alpha_residual faible, coherence globale",
        "measured": {
            "locked_names": list(FINAL_LOCKED_NAMES),
            "frozen_names": list(FINAL_FROZEN_NAMES),
            "internal_ok": evaluation["internal_ok"],
            "theta_supported": internal["theta_supported"],
        },
        "internal": internal,
        "verdict": "supported" if evaluation["internal_ok"] else "falsified",
        "reference": "V15 locked nucleus internal prediction",
    }

    json_path = outdir / f"v16internal_check_{timestamp}.json"
    txt_path = outdir / f"v16internal_check_{timestamp}.txt"
    write_report(json_path, payload)
    txt_lines = [
        "V16 internal check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"z_mod: {internal['z_mod']}",
        f"alpha_residual: {internal['alpha_residual']}",
        f"fine_delta: {internal['fine_delta']}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute internal V16 predictions.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()