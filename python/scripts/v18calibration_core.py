"""Shared helpers for the V18 external fine calibration suite."""
from __future__ import annotations

import json
from pathlib import Path

from v15consolidation_core import FINAL_FROZEN_NAMES, FINAL_LOCKED_NAMES, consolidated_theta, workspace_root
from v16prediction_core import export_prediction
from v17validation_core import analyze_deviation, compare_prediction, evaluate_verdict


CALIBRATION_PROFILES = {
    "calibration_douce": {
        "s_geo": 0.0,
        "s_atom": 0.0,
        "A_kappa": 0.0,
        "p": 0.0,
    },
    "calibration_standard": {
        "s_geo": -0.0005,
        "s_atom": -0.0005,
        "A_kappa": 1.0e-6,
        "p": 0.005,
    },
    "calibration_agressive": {
        "s_geo": -0.001,
        "s_atom": -0.001,
        "A_kappa": 2.0e-6,
        "p": 0.01,
    },
}

PROFILE_ORDER = ["calibration_douce", "calibration_standard", "calibration_agressive"]


def apply_profile(theta: dict[str, float], profile_name: str) -> dict[str, float]:
    adjustments = CALIBRATION_PROFILES[profile_name]
    proposal = dict(theta)
    for name, delta in adjustments.items():
        proposal[name] = theta[name] + delta
    return proposal


def build_profile_payload(profile_name: str, theta_v18: dict[str, float]) -> dict[str, object]:
    v16_payload = export_prediction(theta_v18)
    comparison = compare_prediction(v16_payload)
    deviation = analyze_deviation(comparison)
    verdict = evaluate_verdict(comparison)
    return {
        "profile_name": profile_name,
        "theta_v18": theta_v18,
        "v16": v16_payload,
        "comparison": comparison,
        "deviation": deviation,
        "verdict": verdict["verdict"],
        "supported": verdict["verdict"] == "supported",
        "deviation_score": deviation["deviation_score"],
        "deviation_class": deviation["deviation_class"],
        "internal_ok": bool(v16_payload["internal"]["theta_supported"] and v16_payload["internal"]["alpha_residual"] < 1.0e-8),
        "external_ok": bool(comparison["all_in_bounds"] and comparison["all_signs_ok"]),
        "comparison_ok": bool(comparison["comparison_ok"]),
    }


def baseline_payload() -> dict[str, object]:
    v16_payload = export_prediction()
    comparison = compare_prediction(v16_payload)
    deviation = analyze_deviation(comparison)
    verdict = evaluate_verdict(comparison)
    return {
        "theta_v18": consolidated_theta(),
        "v16": v16_payload,
        "comparison": comparison,
        "deviation": deviation,
        "verdict": verdict["verdict"],
        "deviation_score": deviation["deviation_score"],
        "deviation_class": deviation["deviation_class"],
    }


def select_best_profile(profile_payloads: list[dict[str, object]]) -> dict[str, object]:
    return min(profile_payloads, key=lambda payload: (float(payload["deviation_score"]), payload["profile_name"]))


def v18_result_dir(output_dir: str | Path | None = None) -> Path:
    root = workspace_root()
    return Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")