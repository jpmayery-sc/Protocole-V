"""Verify that the V13 calibrated MAP point repairs the V12 alpha failure."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v13calibration_core import TARGET_THETA, log_posterior, observable_model, run_mcmc, theta_is_supported, workspace_root


def evaluate_postcheck(iterations: int = 5000, burn_in: int = 1000, thin: int = 10, seed: int = 13) -> dict:
	samples, diagnostics = run_mcmc(iterations=iterations, burn_in=burn_in, thin=thin, seed=seed)
	map_theta = diagnostics["map_theta"]
	map_observables = observable_model(map_theta)

	alpha_repaired_ok = map_observables["alpha_residual"] < 1.0e-8
	redshift_ok = (
		1.0e-7 <= map_observables["z_geo"] <= 2.0e-6
		and 1.0e-7 <= map_observables["z_int"] <= 1.0e-5
		and 5.0e-7 <= map_observables["z_canal"] <= 5.0e-6
		and 1.0e-6 <= map_observables["z_mod"] <= 1.0e-5
	)
	fine_ok = 1.0e-6 <= map_observables["fine_delta"] <= 1.0e-3
	theta_supported = theta_is_supported(map_theta)
	posterior_ok = log_posterior(map_theta) > float("-inf")

	verdict = "supported" if alpha_repaired_ok and redshift_ok and fine_ok and theta_supported and posterior_ok else "falsified"

	return {
		"diagnostics": diagnostics,
		"map_theta": map_theta,
		"map_observables": map_observables,
		"alpha_repaired_ok": alpha_repaired_ok,
		"redshift_ok": redshift_ok,
		"fine_ok": fine_ok,
		"theta_supported": theta_supported,
		"posterior_ok": posterior_ok,
		"samples_kept": len(samples),
		"verdict": verdict,
	}


def run_check(output_dir: str | Path | None = None, iterations: int = 5000, burn_in: int = 1000, thin: int = 10, seed: int = 13) -> dict:
	root = workspace_root()
	outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
	outdir.mkdir(parents=True, exist_ok=True)

	timestamp = time.strftime("%Y%m%d-%H%M%SZ")
	result = evaluate_postcheck(iterations=iterations, burn_in=burn_in, thin=thin, seed=seed)

	payload = {
		"timestamp": timestamp,
		"hypothesis": "la calibration MAP de V13 doit reparer V12-ALPHA tout en gardant les autres bornes V12",
		"case_control": "theta MAP",
		"observable": "alpha residual, redshifts internes, correction fine",
		"expected": "alpha reparé, redshifts dans les bornes, correction fine dans la fenetre V12",
		"measured": {
			"alpha_repaired_ok": result["alpha_repaired_ok"],
			"redshift_ok": result["redshift_ok"],
			"fine_ok": result["fine_ok"],
			"theta_supported": result["theta_supported"],
			"posterior_ok": result["posterior_ok"],
			"samples_kept": result["samples_kept"],
		},
		"diagnostics": result["diagnostics"],
		"map_theta": result["map_theta"],
		"map_observables": result["map_observables"],
		"verdict": result["verdict"],
		"reference": "V12 repair check via V13 MAP",
	}

	json_path = outdir / f"v13postcheck_check_{timestamp}.json"
	txt_path = outdir / f"v13postcheck_check_{timestamp}.txt"
	json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

	lines = [
		"V13 postcheck",
		f"timestamp: {timestamp}",
		f"verdict: {result['verdict']}",
		f"alpha_repaired_ok: {result['alpha_repaired_ok']}",
		f"redshift_ok: {result['redshift_ok']}",
		f"fine_ok: {result['fine_ok']}",
		f"theta_supported: {result['theta_supported']}",
		f"posterior_ok: {result['posterior_ok']}",
		f"samples_kept: {result['samples_kept']}",
	]
	txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

	payload["json_path"] = str(json_path)
	payload["txt_path"] = str(txt_path)
	return payload


def main() -> None:
	parser = argparse.ArgumentParser(description="Verify that the V13 calibrated MAP point repairs the V12 alpha failure.")
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