"""Recheck the calibrated chain using the reduced V14 vector."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v13calibration_core import TARGET_THETA, observable_model, workspace_root
from v14reduce_check import evaluate_reduce


def evaluate_recheck(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    reduce_result = evaluate_reduce(outdir)
    full_theta = reduce_result["evaluation"]["full_theta"]
    observables = observable_model(full_theta)

    v11_ok = 1.0e-7 <= observables["z_geo"] <= 2.0e-6 and 1.0e-7 <= observables["z_int"] <= 1.0e-5 and 5.0e-7 <= observables["z_canal"] <= 5.0e-6 and 1.0e-6 <= observables["z_mod"] <= 1.0e-5
    v12_ok = observables["alpha_residual"] < 1.0e-8 and 1.0e-6 <= observables["fine_delta"] <= 1.0e-3
    v13_ok = reduce_result["evaluation"]["supported"]
    verdict = "supported" if v11_ok and v12_ok and v13_ok else "falsified"

    return {
        "reduced_theta": reduce_result["reduced_theta"],
        "full_theta": full_theta,
        "observables": observables,
        "v11_ok": v11_ok,
        "v12_ok": v12_ok,
        "v13_ok": v13_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_recheck(outdir)

    payload = {
        "timestamp": timestamp,
        "hypothesis": "le vecteur reduit conserve la compatibilite V11-V13",
        "case_control": "theta red",
        "observable": "redshifts V11, contraintes V12 et calibration V13",
        "expected": "V11 ok, V12 reparé, V13 ok",
        "measured": {
            "v11_ok": result["v11_ok"],
            "v12_ok": result["v12_ok"],
            "v13_ok": result["v13_ok"],
        },
        "reduced_theta": result["reduced_theta"],
        "full_theta": result["full_theta"],
        "observables": result["observables"],
        "verdict": result["verdict"],
        "reference": "V14 reduced calibration chain",
    }

    json_path = outdir / f"v14recheck_check_{timestamp}.json"
    txt_path = outdir / f"v14recheck_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V14 recheck",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"v11_ok: {result['v11_ok']}",
        f"v12_ok: {result['v12_ok']}",
        f"v13_ok: {result['v13_ok']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Recheck the calibrated chain using the reduced V14 vector.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()