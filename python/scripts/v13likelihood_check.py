"""Check the V13 likelihood against the V12 calibration windows."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v13calibration_core import OBSERVABLE_SIGMAS, TARGET_OBSERVABLES, TARGET_THETA, log_likelihood, observable_model, workspace_root


def evaluate_likelihood() -> dict:
    theta_target = dict(TARGET_THETA)
    theta_perturbed = dict(TARGET_THETA)
    theta_perturbed["alpha0"] += 5.0e-9
    theta_perturbed["s_geo"] += 0.12

    target_observables = observable_model(theta_target)
    perturbed_observables = observable_model(theta_perturbed)
    target_log_likelihood = log_likelihood(theta_target)
    perturbed_log_likelihood = log_likelihood(theta_perturbed)

    alpha_repaired_ok = target_observables["alpha_residual"] < 1.0e-8
    target_better_ok = target_log_likelihood > perturbed_log_likelihood
    finite_ok = math.isfinite(target_log_likelihood) and math.isfinite(perturbed_log_likelihood)
    verdict = "supported" if alpha_repaired_ok and target_better_ok and finite_ok else "falsified"

    return {
        "theta_target": theta_target,
        "theta_perturbed": theta_perturbed,
        "target_observables": target_observables,
        "perturbed_observables": perturbed_observables,
        "target_log_likelihood": target_log_likelihood,
        "perturbed_log_likelihood": perturbed_log_likelihood,
        "alpha_repaired_ok": alpha_repaired_ok,
        "target_better_ok": target_better_ok,
        "finite_ok": finite_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_likelihood()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la vraisemblance V13 doit favoriser la solution qui repare V12-ALPHA",
        "case_control": "theta cible vs theta perturbe",
        "observable": "z_geo, z_int, z_canal, z_mod, alpha_residual, fine_delta",
        "expected": "log-vraisemblance plus haute sur la solution cible, alpha_repaired_ok vrai",
        "measured": {
            "alpha_repaired_ok": result["alpha_repaired_ok"],
            "target_better_ok": result["target_better_ok"],
            "finite_ok": result["finite_ok"],
            "target_log_likelihood": result["target_log_likelihood"],
            "perturbed_log_likelihood": result["perturbed_log_likelihood"],
        },
        "target_observables": result["target_observables"],
        "perturbed_observables": result["perturbed_observables"],
        "sigmas": OBSERVABLE_SIGMAS,
        "targets": TARGET_OBSERVABLES,
        "verdict": result["verdict"],
        "reference": "V12 calibration windows",
    }

    json_path = outdir / f"v13likelihood_check_{timestamp}.json"
    txt_path = outdir / f"v13likelihood_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V13 likelihood check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"alpha_repaired_ok: {result['alpha_repaired_ok']}",
        f"target_better_ok: {result['target_better_ok']}",
        f"finite_ok: {result['finite_ok']}",
        f"target_log_likelihood: {result['target_log_likelihood']:.6f}",
        f"perturbed_log_likelihood: {result['perturbed_log_likelihood']:.6f}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V13 likelihood against the V12 calibration windows.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()