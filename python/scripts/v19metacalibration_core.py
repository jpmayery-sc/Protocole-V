"""Shared helpers for the V19 meta-calibration suite."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from v13calibration_core import ALPHA_REF, PARAMETER_BOUNDS, workspace_root
from v15consolidation_core import consolidated_theta
from v16prediction_core import export_prediction
from v17validation_core import analyze_deviation, compare_prediction, evaluate_verdict
from v18calibration_core import PROFILE_ORDER, apply_profile, build_profile_payload, select_best_profile


MAP_AXIS_ORDER = ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
MAP_OFFSETS = {
    "alpha0": 0.0,
    "s_geo": 5.0e-4,
    "s_atom": 5.0e-4,
    "A_kappa": 1.0e-6,
    "p": 5.0e-3,
}
SENSITIVITY_STEPS = {
    "alpha0": 5.0e-11,
    "s_geo": 5.0e-4,
    "s_atom": 5.0e-4,
    "A_kappa": 1.0e-6,
    "p": 5.0e-3,
}
SENSITIVITY_TARGETS = {
    "alpha0": ("direct", "alpha0_shift"),
    "s_geo": ("internal", "z_geo"),
    "s_atom": ("internal", "z_int"),
    "A_kappa": ("internal", "fine_delta"),
    "p": ("internal", "z_mod"),
}
SUPPORTED_VERDICTS = {"supported", "supported-improved", "supported-neutral", "conforme", "conforme strict"}


def best_v18_profile() -> dict[str, object]:
    theta = consolidated_theta()
    payloads = [build_profile_payload(profile_name, apply_profile(theta, profile_name)) for profile_name in PROFILE_ORDER]
    return select_best_profile(payloads)


def clamp_theta(theta: dict[str, float]) -> dict[str, float]:
    proposal = dict(theta)
    for name, (lower, upper) in PARAMETER_BOUNDS.items():
        proposal[name] = min(max(proposal[name], lower), upper)
    return proposal


def perturb_theta(theta: dict[str, float], name: str, delta: float) -> dict[str, float]:
    proposal = dict(theta)
    proposal[name] = proposal[name] + delta
    return clamp_theta(proposal)


def evaluate_theta(theta: dict[str, float], profile_name: str) -> dict[str, object]:
    payload = build_profile_payload(profile_name, clamp_theta(theta))
    payload["score"] = float(payload["deviation_score"])
    return payload


def evaluate_chain(theta: dict[str, float], profile_name: str) -> dict[str, object]:
    v18_payload = evaluate_theta(theta, profile_name)
    v16_payload = v18_payload["v16"]
    theta_supported = bool(v16_payload["internal"]["theta_supported"])
    chain_length = int(theta_supported) + int(bool(v18_payload["comparison_ok"])) + int(bool(v18_payload["supported"])) + 1
    return {
        "theta": dict(theta),
        "profile_name": profile_name,
        "v18": v18_payload,
        "v17": v18_payload["comparison"],
        "v16": v16_payload,
        "v15_supported": theta_supported,
        "chain_length": chain_length if theta_supported else chain_length - 1,
        "supported": bool(v18_payload["supported"] and v18_payload["comparison_ok"] and theta_supported),
    }


def baseline_payload() -> dict[str, object]:
    best = best_v18_profile()
    theta_reference = dict(best["theta_v18"])
    v16_payload = export_prediction(theta_reference)
    comparison = compare_prediction(v16_payload)
    deviation = analyze_deviation(comparison)
    verdict = evaluate_verdict(comparison)
    return {
        "reference_profile": best,
        "theta_reference": theta_reference,
        "baseline_deviation_score": float(best["deviation_score"]),
        "v16": v16_payload,
        "comparison": comparison,
        "deviation": deviation,
        "verdict": verdict["verdict"],
    }


def build_map_axis(theta_reference: dict[str, float], axis_name: str) -> dict[str, object]:
    baseline_score = float(evaluate_theta(theta_reference, f"v19_map_{axis_name}_center")["deviation_score"])
    axis_samples: list[dict[str, object]] = []
    if axis_name == "alpha0":
        deltas = [0.0]
    else:
        step = MAP_OFFSETS[axis_name]
        deltas = [-step, 0.0, step]

    for delta in deltas:
        sample_theta = perturb_theta(theta_reference, axis_name, delta) if delta else dict(theta_reference)
        position = "center" if delta == 0.0 else ("low" if delta < 0.0 else "high")
        payload = evaluate_theta(sample_theta, f"v19_map_{axis_name}_{position}")
        axis_samples.append(
            {
                "position": position,
                "delta": delta,
                "theta": sample_theta,
                "deviation_score": float(payload["deviation_score"]),
                "deviation_class": payload["deviation_class"],
                "comparison_ok": bool(payload["comparison_ok"]),
                "internal_ok": bool(payload["internal_ok"]),
                "external_ok": bool(payload["external_ok"]),
                "supported": bool(payload["supported"]),
            }
        )

    supported = sum(1 for sample in axis_samples if sample["supported"])
    axis_verdict = "supported"
    if any(not sample["comparison_ok"] for sample in axis_samples):
        axis_verdict = "fragile"
    elif any(sample["deviation_score"] > baseline_score + 0.002 for sample in axis_samples):
        axis_verdict = "supported-partial"

    return {
        "axis": axis_name,
        "baseline_deviation_score": baseline_score,
        "samples": axis_samples,
        "supported_count": supported,
        "total": len(axis_samples),
        "stability_state": "locked" if axis_name == "alpha0" else ("stable" if axis_verdict == "supported" else "narrow" if axis_verdict == "supported-partial" else "dangerous"),
        "verdict": axis_verdict,
    }


def evaluate_map(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    reference = baseline_payload()
    theta = dict(reference["theta_reference"] if theta_reference is None else theta_reference)
    axes = [build_map_axis(theta, axis_name) for axis_name in MAP_AXIS_ORDER]
    samples = [sample for axis in axes for sample in axis["samples"]]
    supported_count = sum(1 for sample in samples if sample["supported"])
    total = len(samples)

    if all(axis["verdict"] == "supported" for axis in axes):
        verdict = "supported"
    elif any(axis["verdict"] == "fragile" for axis in axes):
        verdict = "fragile"
    else:
        verdict = "supported-partial"

    return {
        "reference_profile": reference["reference_profile"],
        "theta_reference": theta,
        "baseline_deviation_score": reference["baseline_deviation_score"],
        "axes": axes,
        "samples": samples,
        "supported_count": supported_count,
        "total": total,
        "supported_ratio": supported_count / max(total, 1),
        "verdict": verdict,
    }


def evaluate_sensitivity(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    reference = baseline_payload()
    theta = dict(reference["theta_reference"] if theta_reference is None else theta_reference)
    rows: list[dict[str, object]] = []

    for parameter_name in MAP_AXIS_ORDER:
        step = SENSITIVITY_STEPS[parameter_name]
        target_scope, target_name = SENSITIVITY_TARGETS[parameter_name]
        low_theta = perturb_theta(theta, parameter_name, -step)
        high_theta = perturb_theta(theta, parameter_name, step)
        low_payload = evaluate_theta(low_theta, f"v19_sensitivity_{parameter_name}_low")
        high_payload = evaluate_theta(high_theta, f"v19_sensitivity_{parameter_name}_high")
        if target_scope == "direct":
            low_value = float(low_theta["alpha0"] - ALPHA_REF)
            high_value = float(high_theta["alpha0"] - ALPHA_REF)
        elif target_scope == "external":
            low_value = float(low_payload["v16"]["external"][target_name])
            high_value = float(high_payload["v16"]["external"][target_name])
        else:
            low_value = float(low_payload["v16"]["internal"][target_name])
            high_value = float(high_payload["v16"]["internal"][target_name])
        derivative = (high_value - low_value) / (2.0 * step)
        rows.append(
            {
                "parameter": parameter_name,
                "step": step,
                "observable": target_name,
                "low_value": low_value,
                "high_value": high_value,
                "derivative": derivative,
                "abs_derivative": abs(derivative),
                "low_supported": bool(low_payload["supported"]),
                "high_supported": bool(high_payload["supported"]),
                "low_comparison_ok": bool(low_payload["comparison_ok"]),
                "high_comparison_ok": bool(high_payload["comparison_ok"]),
            }
        )

    ranking = sorted(rows, key=lambda row: (-row["abs_derivative"], row["parameter"]))
    abs_values = [row["abs_derivative"] for row in ranking]
    median_abs = statistics.median(abs_values)
    top_gap = ranking[0]["abs_derivative"] / max(median_abs, 1.0e-15)
    stable_top2 = len(ranking) >= 2 and ranking[0]["parameter"] != ranking[1]["parameter"]
    dominant = ranking[0]["abs_derivative"] >= 1.2 * median_abs if ranking else False

    if stable_top2 and dominant:
        verdict = "supported"
    elif stable_top2:
        verdict = "supported-partial"
    else:
        verdict = "fragile"

    return {
        "theta_reference": theta,
        "rows": rows,
        "ranking": ranking,
        "top2_stable": stable_top2,
        "dominant_gap": top_gap,
        "median_abs_derivative": median_abs,
        "verdict": verdict,
    }


def evaluate_robust_global(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    reference = baseline_payload()
    theta = dict(reference["theta_reference"] if theta_reference is None else theta_reference)
    map_payload = evaluate_map(theta)
    chain_rows: list[dict[str, object]] = []
    supported_chain_lengths: list[int] = []
    recovery_margins: list[float] = []

    for axis in map_payload["axes"]:
        for sample in axis["samples"]:
            if sample["delta"] == 0.0:
                continue
            chain = evaluate_chain(sample["theta"], f"v19_chain_{axis['axis']}_{sample['position']}")
            chain_rows.append(chain)
            supported_chain_lengths.append(chain["chain_length"])
            if chain["supported"]:
                recovery_margins.append(abs(sample["delta"]))

    supported_chain_length = min(supported_chain_lengths) if supported_chain_lengths else 0
    recovery_margin = min(recovery_margins) if recovery_margins else 0.0
    fragile_layer = "none" if supported_chain_length == 4 else next((row["profile_name"] for row in chain_rows if not row["supported"]), "none")
    bottleneck_flag = supported_chain_length == 4 and recovery_margin < 0.002

    if supported_chain_length == 4 and recovery_margin >= 0.002:
        verdict = "robust"
    elif supported_chain_length == 4:
        verdict = "borderline"
    else:
        verdict = "fragile"

    return {
        "theta_reference": theta,
        "map": map_payload,
        "chain_rows": chain_rows,
        "supported_chain_length": supported_chain_length,
        "fragile_layer": fragile_layer,
        "recovery_margin": recovery_margin,
        "bottleneck_flag": bottleneck_flag,
        "verdict": verdict,
    }


def evaluate_v19_verdict() -> dict[str, object]:
    map_payload = evaluate_map()
    sensitivity_payload = evaluate_sensitivity(map_payload["theta_reference"])
    robust_payload = evaluate_robust_global(map_payload["theta_reference"])

    if map_payload["verdict"] == "supported" and sensitivity_payload["verdict"] == "supported" and robust_payload["verdict"] == "robust":
        verdict = "supported"
        classification = "globalement solide"
    elif map_payload["verdict"] == "supported" and robust_payload["verdict"] == "borderline":
        verdict = "partiel"
        classification = "localement bon"
    elif map_payload["verdict"] == "supported-partial" or sensitivity_payload["verdict"] == "supported-partial":
        verdict = "partiel"
        classification = "trop tendu"
    else:
        verdict = "fragile"
        classification = "fragile"

    return {
        "map": map_payload,
        "sensitivity": sensitivity_payload,
        "robust_global": robust_payload,
        "classification": classification,
        "verdict": verdict,
    }


def v19_result_dir(output_dir: str | Path | None = None) -> Path:
    root = workspace_root()
    return Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")