"""Check the V13 parameter priors and support region."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v13calibration_core import PARAMETER_BOUNDS, PARAMETER_ORDER, TARGET_THETA, within_bounds, workspace_root


def evaluate_params() -> dict:
    bounds_ok = all(lower < upper for lower, upper in PARAMETER_BOUNDS.values())
    target_ok = within_bounds(TARGET_THETA)
    order_ok = list(PARAMETER_BOUNDS.keys()) == PARAMETER_ORDER
    verdict = "supported" if bounds_ok and target_ok and order_ok else "falsified"
    return {
        "bounds_ok": bounds_ok,
        "target_ok": target_ok,
        "order_ok": order_ok,
        "theta": TARGET_THETA,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_params()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "les hyperparametres V13 doivent rester dans des priors bornes et inclure la solution cible",
        "case_control": "aE, aR, A_kappa, p, alpha0, s_geo, s_atom, s_canal",
        "observable": "vecteur theta",
        "expected": "bornes valides, ordre stable, theta cible dans le support",
        "measured": {
            "bounds_ok": result["bounds_ok"],
            "target_ok": result["target_ok"],
            "order_ok": result["order_ok"],
        },
        "theta": result["theta"],
        "bounds": PARAMETER_BOUNDS,
        "verdict": result["verdict"],
        "reference": "V13 parameter vector",
    }

    json_path = outdir / f"v13params_check_{timestamp}.json"
    txt_path = outdir / f"v13params_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V13 params check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"bounds_ok: {result['bounds_ok']}",
        f"target_ok: {result['target_ok']}",
        f"order_ok: {result['order_ok']}",
        "",
        "Theta:",
    ]
    for name in PARAMETER_ORDER:
        lines.append(f"- {name}: {TARGET_THETA[name]}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V13 parameter priors and support region.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()