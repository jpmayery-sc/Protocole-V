"""Run the V13 Metropolis-Hastings calibration sampler."""
from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path

from v13calibration_core import (
    PARAMETER_ORDER,
    TARGET_OBSERVABLES,
    log_posterior,
    observable_model,
    posterior_covariance,
    posterior_observable_summary,
    run_mcmc,
    summarize_samples,
    theta_is_supported,
    workspace_root,
)


def evaluate_mcmc(iterations: int = 5000, burn_in: int = 1000, thin: int = 10, seed: int = 13) -> dict:
    samples, diagnostics = run_mcmc(iterations=iterations, burn_in=burn_in, thin=thin, seed=seed)
    summary = summarize_samples(samples)
    covariance = posterior_covariance(samples)
    map_theta = diagnostics["map_theta"]
    posterior_mean = {name: summary[name]["mean"] for name in PARAMETER_ORDER}

    map_supported = theta_is_supported(map_theta)
    mean_supported = theta_is_supported(posterior_mean)
    acceptance_ok = 0.15 <= diagnostics["acceptance_rate"] <= 0.85
    samples_ok = len(samples) >= 200
    likelihood_gain_ok = diagnostics["best_log_posterior"] >= diagnostics["final_log_posterior"] - 10.0
    verdict = "supported" if map_supported and mean_supported and acceptance_ok and samples_ok and likelihood_gain_ok else "falsified"

    return {
        "diagnostics": diagnostics,
        "summary": summary,
        "covariance": covariance,
        "posterior_mean": posterior_mean,
        "map_theta": map_theta,
        "posterior_mean_observables": posterior_observable_summary(posterior_mean),
        "map_observables": posterior_observable_summary(map_theta),
        "acceptance_ok": acceptance_ok,
        "samples_ok": samples_ok,
        "likelihood_gain_ok": likelihood_gain_ok,
        "map_supported": map_supported,
        "mean_supported": mean_supported,
        "samples_kept": len(samples),
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None, iterations: int = 5000, burn_in: int = 1000, thin: int = 10, seed: int = 13) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_mcmc(iterations=iterations, burn_in=burn_in, thin=thin, seed=seed)

    payload = {
        "timestamp": timestamp,
        "hypothesis": "un MCMC court doit concentrer la posteriore sur la region qui repare V12-ALPHA",
        "case_control": "theta cible, posterior mean, MAP",
        "observable": "diagnostics de chaine et observables calibres",
        "expected": "acceptation raisonnable, echantillons suffisants, theta MAP supporte et theta moyen supporte",
        "measured": {
            "acceptance_rate": result["diagnostics"]["acceptance_rate"],
            "samples_kept": result["samples_kept"],
            "map_supported": result["map_supported"],
            "mean_supported": result["mean_supported"],
            "acceptance_ok": result["acceptance_ok"],
            "samples_ok": result["samples_ok"],
            "likelihood_gain_ok": result["likelihood_gain_ok"],
        },
        "diagnostics": result["diagnostics"],
        "posterior_mean": result["posterior_mean"],
        "map_theta": result["map_theta"],
        "posterior_mean_observables": result["posterior_mean_observables"],
        "map_observables": result["map_observables"],
        "summary": result["summary"],
        "covariance": result["covariance"],
        "targets": TARGET_OBSERVABLES,
        "verdict": result["verdict"],
        "reference": "V13 MCMC calibration on V12 windows",
    }

    json_path = outdir / f"v13mcmc_check_{timestamp}.json"
    txt_path = outdir / f"v13mcmc_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V13 MCMC check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"acceptance_rate: {result['diagnostics']['acceptance_rate']:.3f}",
        f"samples_kept: {result['samples_kept']}",
        f"map_supported: {result['map_supported']}",
        f"mean_supported: {result['mean_supported']}",
        f"acceptance_ok: {result['acceptance_ok']}",
        f"samples_ok: {result['samples_ok']}",
        f"likelihood_gain_ok: {result['likelihood_gain_ok']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V13 Metropolis-Hastings calibration sampler.")
    parser.add_argument("--output-dir", default=None)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--burn-in", type=int, default=1000)
    parser.add_argument("--thin", type=int, default=10)
    parser.add_argument("--seed", type=int, default=13)
    args = parser.parse_args()

    result = run_check(args.output_dir, iterations=args.iterations, burn_in=args.burn_in, thin=args.thin, seed=args.seed)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()