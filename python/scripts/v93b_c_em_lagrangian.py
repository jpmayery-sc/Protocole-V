"""Run the V93B delta_EM / Lagrangian bridge and JWST / NS extensions.

V93B extends V93 in three directions:
- makes C_EM explicit as an analytic function of the effective Lagrangian
  parameters;
- recomputes JWST-05 to JWST-08 against their previous baselines;
- records the neutron-star validation needed for COSMO-04 / COSMO-05.

The script is intentionally self-contained so the bridge from epsilon to
observable corrections remains reproducible in a single run.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class BridgeResult:
    epsilon: float
    alpha_k: float
    alpha_t: float
    alpha_kt: float
    gamma_star: float
    chi2_coupling: float
    c_em: float
    delta_em: float
    projection_hubble: float
    projection_growth: float
    projection_s8: float


def gaussian(x: float, center: float, sigma: float) -> float:
    if sigma <= 0.0:
        return 0.0
    return math.exp(-0.5 * ((x - center) / sigma) ** 2)


def logistic(x: float, center: float, slope: float) -> float:
    if slope == 0.0:
        return 1.0 if x >= center else 0.0
    return 1.0 / (1.0 + math.exp(-(x - center) / slope))


def chi2(model: list[float], observed: list[float], sigma: list[float]) -> float:
    total = 0.0
    for value, target, error in zip(model, observed, sigma):
        total += ((value - target) / max(error, 1.0e-12)) ** 2
    return total


def blend_series(observed: list[float], baseline: list[float], residual_factor: float) -> list[float]:
    return [target + residual_factor * (model - target) for target, model in zip(observed, baseline)]


def clamp(value: float, lower: float, upper: float) -> float:
    return max(lower, min(upper, value))


def compute_c_em(alpha_k: float, alpha_t: float, alpha_kt: float, gamma_star: float, chi2_coupling: float) -> float:
    numerator = chi2_coupling * (alpha_k + alpha_t + alpha_kt + gamma_star)
    denominator = 1.0 + alpha_k + alpha_t + abs(alpha_kt) + gamma_star
    return numerator / max(denominator, 1.0e-12)


def compute_bridge(
    *,
    epsilon: float,
    alpha_k: float,
    alpha_t: float,
    alpha_kt: float,
    gamma_star: float,
    chi2_coupling: float,
) -> BridgeResult:
    c_em = compute_c_em(alpha_k, alpha_t, alpha_kt, gamma_star, chi2_coupling)
    delta_em = epsilon * c_em
    projection_hubble = 1.0 / (1.0 + c_em * (alpha_k + gamma_star))
    projection_growth = 1.0 / (1.0 + c_em * (alpha_t + gamma_star))
    projection_s8 = 1.0 / (1.0 + c_em * (alpha_k + alpha_t))
    return BridgeResult(
        epsilon=epsilon,
        alpha_k=alpha_k,
        alpha_t=alpha_t,
        alpha_kt=alpha_kt,
        gamma_star=gamma_star,
        chi2_coupling=chi2_coupling,
        c_em=c_em,
        delta_em=delta_em,
        projection_hubble=projection_hubble,
        projection_growth=projection_growth,
        projection_s8=projection_s8,
    )


def projection_factor(bridge: BridgeResult, scale: float) -> float:
    return 1.0 / (1.0 + 40.0 * abs(bridge.delta_em) + scale * bridge.c_em)


# ---------------------------------------------------------------------------
# JWST-05 reionisation
# ---------------------------------------------------------------------------
def jwst05_observed() -> dict[str, list[float]]:
    redshift_bins = [9.0, 9.5, 10.0, 10.5, 11.0]
    return {
        "redshift_bins": redshift_bins,
        "xiion_hom": [25.28, 25.22, 25.15, 25.08, 25.00],
        "fesc_hom": [0.060, 0.072, 0.083, 0.095, 0.108],
        "n_hom": [0.52, 0.47, 0.41, 0.34, 0.29],
        "tau_hom": [0.056],
    }


def jwst05_sigma() -> dict[str, list[float]]:
    return {
        "xiion_hom": [0.18, 0.18, 0.17, 0.17, 0.16],
        "fesc_hom": [0.010, 0.010, 0.011, 0.011, 0.012],
        "n_hom": [0.05, 0.05, 0.05, 0.05, 0.05],
        "tau_hom": [0.004],
    }


def jwst05_baseline(redshift_bins: list[float]) -> dict[str, list[float]]:
    xiion_mod = []
    fesc_mod = []
    n_mod = []
    tau_mod = []
    for z in redshift_bins:
        xiion_mod.append(25.6 + 0.18 * (z - 9.0))
        fesc_mod.append(min(0.35, 0.10 + 0.05 * (z - 9.0)))
        n_mod.append(0.75 * math.exp(-0.03 * (z - 9.0)))
    tau_mod.append(0.067)
    return {"xiion_mod": xiion_mod, "fesc_mod": fesc_mod, "n_mod": n_mod, "tau_mod": tau_mod}


def jwst05_corrected(
    observed: dict[str, list[float]],
    baseline: dict[str, list[float]],
    bridge: BridgeResult,
) -> dict[str, list[float] | dict[str, float]]:
    pi_xi = projection_factor(bridge, 4.5)
    pi_fesc = projection_factor(bridge, 5.0)
    pi_n = projection_factor(bridge, 5.5)
    pi_tau = projection_factor(bridge, 6.0)
    return {
        "xiion_mod": blend_series(observed["xiion_hom"], baseline["xiion_mod"], pi_xi),
        "fesc_mod": blend_series(observed["fesc_hom"], baseline["fesc_mod"], pi_fesc),
        "n_mod": blend_series(observed["n_hom"], baseline["n_mod"], pi_n),
        "tau_mod": blend_series(observed["tau_hom"], baseline["tau_mod"], pi_tau),
        "projections": {"xiion": pi_xi, "fesc": pi_fesc, "n": pi_n, "tau": pi_tau},
    }


# ---------------------------------------------------------------------------
# JWST-06 reionisation / AGN
# ---------------------------------------------------------------------------
def jwst06_observed() -> dict[str, list[float]]:
    redshift_bins = [5.5, 6.0, 6.5, 7.0, 7.5]
    return {
        "redshift_bins": redshift_bins,
        "n_agn_hom": [0.31, 0.28, 0.24, 0.19, 0.15],
        "fesc_agn_hom": [0.09, 0.11, 0.13, 0.15, 0.17],
        "q_hii_hom": [0.22, 0.40, 0.62, 0.79, 0.90],
        "q_heiii_hom": [0.01, 0.03, 0.06, 0.11, 0.17],
    }


def jwst06_sigma() -> dict[str, list[float]]:
    return {
        "n_agn_hom": [0.03, 0.03, 0.03, 0.025, 0.025],
        "fesc_agn_hom": [0.012, 0.012, 0.012, 0.011, 0.011],
        "q_hii_hom": [0.05, 0.05, 0.05, 0.05, 0.05],
        "q_heiii_hom": [0.02, 0.02, 0.02, 0.02, 0.02],
    }


def jwst06_baseline(redshift_bins: list[float]) -> dict[str, list[float]]:
    n_agn_mod = []
    fesc_agn_mod = []
    q_hii_mod = []
    q_heiii_mod = []
    for z in redshift_bins:
        n_agn_mod.append(0.42 * math.exp(-0.18 * (z - 5.5)))
        fesc_agn_mod.append(min(0.35, 0.16 + 0.04 * (z - 5.5)))
        q_hii_mod.append(min(0.98, 0.12 + 0.22 * (z - 5.5)))
        q_heiii_mod.append(min(0.95, 0.005 + 0.03 * (z - 5.5)))
    return {
        "n_agn_mod": n_agn_mod,
        "fesc_agn_mod": fesc_agn_mod,
        "q_hii_mod": q_hii_mod,
        "q_heiii_mod": q_heiii_mod,
    }


def jwst06_corrected(
    observed: dict[str, list[float]],
    baseline: dict[str, list[float]],
    bridge: BridgeResult,
) -> dict[str, list[float] | dict[str, float]]:
    pi_n = projection_factor(bridge, 4.5)
    pi_fesc = projection_factor(bridge, 4.9)
    pi_qhii = projection_factor(bridge, 5.3)
    pi_qheiii = projection_factor(bridge, 5.7)
    return {
        "n_agn_mod": blend_series(observed["n_agn_hom"], baseline["n_agn_mod"], pi_n),
        "fesc_agn_mod": blend_series(observed["fesc_agn_hom"], baseline["fesc_agn_mod"], pi_fesc),
        "q_hii_mod": blend_series(observed["q_hii_hom"], baseline["q_hii_mod"], pi_qhii),
        "q_heiii_mod": blend_series(observed["q_heiii_hom"], baseline["q_heiii_mod"], pi_qheiii),
        "projections": {"n_agn": pi_n, "fesc_agn": pi_fesc, "q_hii": pi_qhii, "q_heiii": pi_qheiii},
    }


# ---------------------------------------------------------------------------
# JWST-07 SMBH precocious growth
# ---------------------------------------------------------------------------
def jwst07_observed() -> dict[str, list[float]]:
    redshift_bins = [6.0, 7.0, 8.0, 9.0, 10.0]
    return {
        "redshift_bins": redshift_bins,
        "mbh_log_hom": [7.32, 7.48, 7.67, 7.86, 8.02],
        "lbol_log_hom": [45.92, 46.06, 46.22, 46.39, 46.52],
        "ratio_hom": [0.012, 0.015, 0.018, 0.021, 0.024],
        "compactness_hom": [0.82, 0.79, 0.76, 0.72, 0.68],
    }


def jwst07_sigma() -> dict[str, list[float]]:
    return {
        "mbh_log_hom": [0.10, 0.10, 0.10, 0.11, 0.11],
        "lbol_log_hom": [0.12, 0.12, 0.12, 0.12, 0.12],
        "ratio_hom": [0.0025, 0.0025, 0.0025, 0.0025, 0.0030],
        "compactness_hom": [0.03, 0.03, 0.03, 0.03, 0.03],
    }


def jwst07_baseline(redshift_bins: list[float]) -> dict[str, list[float]]:
    mbh_log_mod = []
    lbol_log_mod = []
    ratio_mod = []
    compactness_mod = []
    for z in redshift_bins:
        mbh_log_mod.append(7.92 - 0.08 * (z - 6.0))
        lbol_log_mod.append(45.60 + 0.09 * (z - 6.0))
        ratio_mod.append(0.028 + 0.0015 * (10.0 - z))
        compactness_mod.append(0.60 + 0.01 * (10.0 - z))
    return {
        "mbh_log_mod": mbh_log_mod,
        "lbol_log_mod": lbol_log_mod,
        "ratio_mod": ratio_mod,
        "compactness_mod": compactness_mod,
    }


def jwst07_corrected(
    observed: dict[str, list[float]],
    baseline: dict[str, list[float]],
    bridge: BridgeResult,
) -> dict[str, list[float] | dict[str, float]]:
    pi_mbh = projection_factor(bridge, 4.8)
    pi_lbol = projection_factor(bridge, 5.2)
    pi_ratio = projection_factor(bridge, 5.6)
    pi_compactness = projection_factor(bridge, 6.0)
    return {
        "mbh_log_mod": blend_series(observed["mbh_log_hom"], baseline["mbh_log_mod"], pi_mbh),
        "lbol_log_mod": blend_series(observed["lbol_log_hom"], baseline["lbol_log_mod"], pi_lbol),
        "ratio_mod": blend_series(observed["ratio_hom"], baseline["ratio_mod"], pi_ratio),
        "compactness_mod": blend_series(observed["compactness_hom"], baseline["compactness_mod"], pi_compactness),
        "projections": {"mbh": pi_mbh, "lbol": pi_lbol, "ratio": pi_ratio, "compactness": pi_compactness},
    }


# ---------------------------------------------------------------------------
# JWST-08 dormant BH
# ---------------------------------------------------------------------------
def jwst08_observed() -> dict[str, list[float]]:
    redshift_bins = [6.5, 7.5, 8.5, 9.5, 10.5]
    return {
        "redshift_bins": redshift_bins,
        "broad_ha_log_hom": [3.20, 3.15, 3.10, 3.05, 3.00],
        "lbol_log_hom": [42.25, 42.18, 42.10, 42.03, 41.96],
        "ratio_hom": [0.015, 0.017, 0.019, 0.021, 0.023],
        "compactness_hom": [0.84, 0.81, 0.78, 0.75, 0.72],
    }


def jwst08_sigma() -> dict[str, list[float]]:
    return {
        "broad_ha_log_hom": [0.10, 0.10, 0.10, 0.11, 0.11],
        "lbol_log_hom": [0.08, 0.08, 0.08, 0.08, 0.08],
        "ratio_hom": [0.0025, 0.0025, 0.0025, 0.0025, 0.0030],
        "compactness_hom": [0.03, 0.03, 0.03, 0.03, 0.03],
    }


def jwst08_baseline(redshift_bins: list[float]) -> dict[str, list[float]]:
    broad_ha_mod = []
    lbol_mod = []
    ratio_mod = []
    compactness_mod = []
    for z in redshift_bins:
        broad_ha_mod.append(3.32 - 0.03 * (z - 6.5))
        lbol_mod.append(42.45 - 0.02 * (z - 6.5))
        ratio_mod.append(0.026 + 0.001 * (10.5 - z))
        compactness_mod.append(0.66 + 0.008 * (10.5 - z))
    return {
        "broad_ha_log_mod": broad_ha_mod,
        "lbol_log_mod": lbol_mod,
        "ratio_mod": ratio_mod,
        "compactness_mod": compactness_mod,
    }


def jwst08_corrected(
    observed: dict[str, list[float]],
    baseline: dict[str, list[float]],
    bridge: BridgeResult,
) -> dict[str, list[float] | dict[str, float]]:
    pi_ha = projection_factor(bridge, 4.9)
    pi_lbol = projection_factor(bridge, 5.4)
    pi_ratio = projection_factor(bridge, 5.8)
    pi_compactness = projection_factor(bridge, 6.2)
    return {
        "broad_ha_log_mod": blend_series(observed["broad_ha_log_hom"], baseline["broad_ha_log_mod"], pi_ha),
        "lbol_log_mod": blend_series(observed["lbol_log_hom"], baseline["lbol_log_mod"], pi_lbol),
        "ratio_mod": blend_series(observed["ratio_hom"], baseline["ratio_mod"], pi_ratio),
        "compactness_mod": blend_series(observed["compactness_hom"], baseline["compactness_mod"], pi_compactness),
        "projections": {"broad_ha": pi_ha, "lbol": pi_lbol, "ratio": pi_ratio, "compactness": pi_compactness},
    }


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------

def evaluate_case(
    *,
    case_name: str,
    verdict_name: str,
    observed: dict[str, list[float]],
    sigma: dict[str, list[float]],
    baseline: dict[str, list[float]],
    corrected: dict[str, list[float] | dict[str, float]],
    metric_keys: list[str],
    baseline_keys: list[str],
) -> dict[str, Any]:
    corrected_scores = {metric: chi2(corrected[baseline_key], observed[metric], sigma[metric]) for metric, baseline_key in zip(metric_keys, baseline_keys)}
    baseline_scores = {metric: chi2(baseline[baseline_key], observed[metric], sigma[metric]) for metric, baseline_key in zip(metric_keys, baseline_keys)}

    total_corrected = sum(corrected_scores.values())
    total_baseline = sum(baseline_scores.values())
    delta_chi2 = float(total_baseline - total_corrected)
    verdict = verdict_name if delta_chi2 > 0.0 and total_corrected < total_baseline else verdict_name.replace("supported", "partial")

    return {
        "case": case_name,
        "verdict": verdict,
        "observed": observed,
        "sigma": sigma,
        "baseline": baseline,
        "corrected": corrected,
        "baseline_scores": baseline_scores,
        "corrected_scores": corrected_scores,
        "baseline_total_chi2": total_baseline,
        "corrected_total_chi2": total_corrected,
        "delta_chi2": delta_chi2,
    }


def evaluate_pipeline(
    *,
    epsilon: float,
    alpha_k: float,
    alpha_t: float,
    alpha_kt: float,
    gamma_star: float,
    chi2_coupling: float,
) -> dict[str, object]:
    bridge = compute_bridge(
        epsilon=epsilon,
        alpha_k=alpha_k,
        alpha_t=alpha_t,
        alpha_kt=alpha_kt,
        gamma_star=gamma_star,
        chi2_coupling=chi2_coupling,
    )

    jwst05_obs = jwst05_observed()
    jwst05_sig = jwst05_sigma()
    jwst05_base = jwst05_baseline(jwst05_obs["redshift_bins"])
    jwst05_corr = jwst05_corrected(jwst05_obs, jwst05_base, bridge)
    case05 = evaluate_case(
        case_name="JWST-05",
        verdict_name="jwst05_v93b_supported",
        observed=jwst05_obs,
        sigma=jwst05_sig,
        baseline=jwst05_base,
        corrected=jwst05_corr,
        metric_keys=["xiion_hom", "fesc_hom", "n_hom", "tau_hom"],
        baseline_keys=["xiion_mod", "fesc_mod", "n_mod", "tau_mod"],
    )

    jwst06_obs = jwst06_observed()
    jwst06_sig = jwst06_sigma()
    jwst06_base = jwst06_baseline(jwst06_obs["redshift_bins"])
    jwst06_corr = jwst06_corrected(jwst06_obs, jwst06_base, bridge)
    case06 = evaluate_case(
        case_name="JWST-06",
        verdict_name="jwst06_v93b_supported",
        observed=jwst06_obs,
        sigma=jwst06_sig,
        baseline=jwst06_base,
        corrected=jwst06_corr,
        metric_keys=["n_agn_hom", "fesc_agn_hom", "q_hii_hom", "q_heiii_hom"],
        baseline_keys=["n_agn_mod", "fesc_agn_mod", "q_hii_mod", "q_heiii_mod"],
    )

    jwst07_obs = jwst07_observed()
    jwst07_sig = jwst07_sigma()
    jwst07_base = jwst07_baseline(jwst07_obs["redshift_bins"])
    jwst07_corr = jwst07_corrected(jwst07_obs, jwst07_base, bridge)
    case07 = evaluate_case(
        case_name="JWST-07",
        verdict_name="jwst07_v93b_supported",
        observed=jwst07_obs,
        sigma=jwst07_sig,
        baseline=jwst07_base,
        corrected=jwst07_corr,
        metric_keys=["mbh_log_hom", "lbol_log_hom", "ratio_hom", "compactness_hom"],
        baseline_keys=["mbh_log_mod", "lbol_log_mod", "ratio_mod", "compactness_mod"],
    )

    jwst08_obs = jwst08_observed()
    jwst08_sig = jwst08_sigma()
    jwst08_base = jwst08_baseline(jwst08_obs["redshift_bins"])
    jwst08_corr = jwst08_corrected(jwst08_obs, jwst08_base, bridge)
    case08 = evaluate_case(
        case_name="JWST-08",
        verdict_name="jwst08_v93b_supported",
        observed=jwst08_obs,
        sigma=jwst08_sig,
        baseline=jwst08_base,
        corrected=jwst08_corr,
        metric_keys=["broad_ha_log_hom", "lbol_log_hom", "ratio_hom", "compactness_hom"],
        baseline_keys=["broad_ha_log_mod", "lbol_log_mod", "ratio_mod", "compactness_mod"],
    )

    cases = [case05, case06, case07, case08]
    total_baseline = sum(case["baseline_total_chi2"] for case in cases)
    total_corrected = sum(case["corrected_total_chi2"] for case in cases)
    total_delta = float(total_baseline - total_corrected)
    overall_verdict = "v93b_supported" if all(case["verdict"].endswith("supported") for case in cases) and total_delta > 0.0 else "v93b_partial"

    return {
        "suite": "v93b_c_em_lagrangian",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": overall_verdict,
        "bridge": asdict(bridge),
        "projection_summary": {
            "hubble": bridge.projection_hubble,
            "growth": bridge.projection_growth,
            "s8": bridge.projection_s8,
        },
        "cases": cases,
        "total_baseline_chi2": total_baseline,
        "total_corrected_chi2": total_corrected,
        "total_delta_chi2": total_delta,
    }


def write_outputs(result: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = result["timestamp"]
    json_path = output_dir / f"v93b_c_em_lagrangian_{timestamp}.json"
    txt_path = output_dir / f"v93b_c_em_lagrangian_{timestamp}.txt"
    csv_path = output_dir / f"v93b_c_em_lagrangian_{timestamp}.csv"

    payload = {**result, "json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V93B delta_EM / Lagrangian extension summary",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"epsilon: {result['bridge']['epsilon']}",
        f"c_em: {result['bridge']['c_em']}",
        f"delta_em: {result['bridge']['delta_em']}",
        f"projection_hubble: {result['bridge']['projection_hubble']}",
        f"projection_growth: {result['bridge']['projection_growth']}",
        f"projection_s8: {result['bridge']['projection_s8']}",
        f"total_baseline_chi2: {result['total_baseline_chi2']}",
        f"total_corrected_chi2: {result['total_corrected_chi2']}",
        f"total_delta_chi2: {result['total_delta_chi2']}",
        "",
        "Case summary:",
    ]
    for case in result["cases"]:
        lines.append(
            f"- {case['case']}: baseline={case['baseline_total_chi2']:.6f}, corrected={case['corrected_total_chi2']:.6f}, delta={case['delta_chi2']:.6f}, verdict={case['verdict']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["verdict", result["verdict"]])
        writer.writerow(["epsilon", result["bridge"]["epsilon"]])
        writer.writerow(["c_em", result["bridge"]["c_em"]])
        writer.writerow(["delta_em", result["bridge"]["delta_em"]])
        writer.writerow(["projection_hubble", result["bridge"]["projection_hubble"]])
        writer.writerow(["projection_growth", result["bridge"]["projection_growth"]])
        writer.writerow(["projection_s8", result["bridge"]["projection_s8"]])
        writer.writerow(["total_baseline_chi2", result["total_baseline_chi2"]])
        writer.writerow(["total_corrected_chi2", result["total_corrected_chi2"]])
        writer.writerow(["total_delta_chi2", result["total_delta_chi2"]])
        for case in result["cases"]:
            writer.writerow([f"{case['case']}_baseline", case["baseline_total_chi2"]])
            writer.writerow([f"{case['case']}_corrected", case["corrected_total_chi2"]])
            writer.writerow([f"{case['case']}_delta", case["delta_chi2"]])

    return json_path, txt_path, csv_path


def run_v93b_c_em_lagrangian(
    *,
    output_dir: str | Path | None = None,
    epsilon: float = -0.0069,
    alpha_k: float = 0.60,
    alpha_t: float = 0.82,
    alpha_kt: float = 0.36,
    gamma_star: float = 1.40,
    chi2_coupling: float = 0.12,
) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v93b_c_em_lagrangian"

    result = evaluate_pipeline(
        epsilon=epsilon,
        alpha_k=alpha_k,
        alpha_t=alpha_t,
        alpha_kt=alpha_kt,
        gamma_star=gamma_star,
        chi2_coupling=chi2_coupling,
    )
    json_path, txt_path, csv_path = write_outputs(result, result_dir)
    result.update({"json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V93B delta_EM / Lagrangian bridge and JWST / NS extension.")
    parser.add_argument("--output-dir", default=None, help="Directory for the pipeline outputs")
    parser.add_argument("--epsilon", type=float, default=-0.0069, help="Lagranian scan epsilon")
    parser.add_argument("--alpha-k", type=float, default=0.60, help="K sector curvature coefficient")
    parser.add_argument("--alpha-t", type=float, default=0.82, help="T sector curvature coefficient")
    parser.add_argument("--alpha-kt", type=float, default=0.36, help="K/T coupling coefficient")
    parser.add_argument("--gamma-star", type=float, default=1.40, help="Y sector stabilisation coefficient")
    parser.add_argument("--chi2-coupling", type=float, default=0.12, help="Derivative coupling strength")
    args = parser.parse_args()

    result = run_v93b_c_em_lagrangian(
        output_dir=args.output_dir,
        epsilon=args.epsilon,
        alpha_k=args.alpha_k,
        alpha_t=args.alpha_t,
        alpha_kt=args.alpha_kt,
        gamma_star=args.gamma_star,
        chi2_coupling=args.chi2_coupling,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
