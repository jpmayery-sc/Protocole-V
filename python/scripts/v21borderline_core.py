"""Shared helpers for the V21 borderline-resolution suite."""
from __future__ import annotations

import json
from pathlib import Path

from v19metacalibration_core import (
    best_v18_profile,
    evaluate_map,
    evaluate_robust_global,
    evaluate_sensitivity,
    v19_result_dir,
)


def v21_reference_theta() -> dict[str, float]:
    best = best_v18_profile()
    return dict(best["theta_v18"])


def evaluate_borderline(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v21_reference_theta() if theta_reference is None else dict(theta_reference)
    robust = evaluate_robust_global(theta)
    borderline = robust["verdict"] == "borderline"
    recovery_margin = float(robust["recovery_margin"])
    supported_chain_length = int(robust["supported_chain_length"])
    fragile_layer = robust["fragile_layer"]
    bottleneck_flag = bool(robust["bottleneck_flag"])
    classification = "localement bon" if borderline else ("fragile" if robust["verdict"] == "fragile" else "globalement solide")
    verdict = "supported" if supported_chain_length == 4 and fragile_layer == "none" else "supported-partial" if supported_chain_length == 4 else "fragile"

    return {
        "theta_reference": theta,
        "robust_global": robust,
        "classification": classification,
        "supported_chain_length": supported_chain_length,
        "fragile_layer": fragile_layer,
        "recovery_margin": recovery_margin,
        "bottleneck_flag": bottleneck_flag,
        "borderline": borderline,
        "verdict": verdict,
    }


def evaluate_recovery(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    borderline = evaluate_borderline(theta_reference)
    recovery_margin = float(borderline["recovery_margin"])
    supported_chain_length = int(borderline["supported_chain_length"])
    bottleneck_flag = bool(borderline["bottleneck_flag"])
    recovery_depth = recovery_margin / 0.002 if recovery_margin else 0.0
    resolution_score = supported_chain_length + (1 if bottleneck_flag else 0) + recovery_depth

    if supported_chain_length == 4 and bottleneck_flag:
        verdict = "supported"
    elif supported_chain_length == 4:
        verdict = "supported-partial"
    else:
        verdict = "fragile"

    return {
        "theta_reference": dict(v21_reference_theta() if theta_reference is None else theta_reference),
        "borderline": borderline,
        "recovery_margin": recovery_margin,
        "recovery_depth": recovery_depth,
        "resolution_score": resolution_score,
        "supported_chain_length": supported_chain_length,
        "bottleneck_flag": bottleneck_flag,
        "verdict": verdict,
    }


def evaluate_resolution(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v21_reference_theta() if theta_reference is None else dict(theta_reference)
    map_payload = evaluate_map(theta)
    sensitivity_payload = evaluate_sensitivity(theta)
    robust_payload = evaluate_robust_global(theta)

    map_verdict = map_payload["verdict"]
    sensitivity_verdict = sensitivity_payload["verdict"]
    robust_verdict = robust_payload["verdict"]

    if map_verdict == "supported" and sensitivity_verdict == "supported" and robust_verdict == "borderline":
        resolution_state = "resolu"
        resolution_confidence = "haute"
        verdict = "supported"
    elif map_verdict == "supported" and sensitivity_verdict in {"supported", "supported-partial"} and robust_verdict == "borderline":
        resolution_state = "partiellement_resolu"
        resolution_confidence = "moyenne"
        verdict = "supported-partial"
    else:
        resolution_state = "fragile"
        resolution_confidence = "faible"
        verdict = "fragile"

    return {
        "theta_reference": theta,
        "map": map_payload,
        "sensitivity": sensitivity_payload,
        "robust_global": robust_payload,
        "map_verdict": map_verdict,
        "sensitivity_verdict": sensitivity_verdict,
        "robust_verdict": robust_verdict,
        "resolution_state": resolution_state,
        "resolution_confidence": resolution_confidence,
        "verdict": verdict,
    }


def evaluate_v21_verdict(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    borderline = evaluate_borderline(theta_reference)
    recovery = evaluate_recovery(theta_reference)
    resolution = evaluate_resolution(theta_reference)

    if borderline["verdict"] == "supported" and recovery["verdict"] == "supported" and resolution["verdict"] == "supported":
        verdict_global = "supported"
        classification = "resolu"
    elif borderline["verdict"] in {"supported", "supported-partial"} and resolution["verdict"] == "supported-partial":
        verdict_global = "supported-partial"
        classification = "partiellement_resolu"
    else:
        verdict_global = "fragile"
        classification = "fragile"

    return {
        "borderline": borderline,
        "recovery": recovery,
        "resolution": resolution,
        "verdict_global": verdict_global,
        "classification": classification,
        "niveau_de_confiance": resolution["resolution_confidence"],
        "zone_critique_principale": borderline["fragile_layer"],
        "verdict": verdict_global,
    }


def v21_result_dir(output_dir: str | Path | None = None) -> Path:
    return Path(output_dir) if output_dir is not None else v19_result_dir()


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")