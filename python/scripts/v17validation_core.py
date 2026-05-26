"""Shared helpers for the V17 external validation suite."""
from __future__ import annotations

import json
import math
from pathlib import Path

from v16prediction_core import export_prediction, result_dir as v16_result_dir
from v15consolidation_core import FINAL_FROZEN_NAMES, FINAL_LOCKED_NAMES, workspace_root


REFERENCE_ORDER = ["z_obs", "delta_nu_over_nu", "delta_E", "fine_correction_eff", "grav_torsion_eff"]
REFERENCE_BOUNDS = {
    "z_obs": (1.0e-4, 1.5e-4),
    "delta_nu_over_nu": (2.5e-5, 3.5e-5),
    "delta_E": (2.0e-5, 2.8e-5),
    "fine_correction_eff": (1.5, 2.5),
    "grav_torsion_eff": (-2.0e-4, 0.0),
}
REFERENCE_TARGETS = {
    "z_obs": 1.25e-4,
    "delta_nu_over_nu": 2.85e-5,
    "delta_E": 2.40e-5,
    "fine_correction_eff": 2.0,
    "grav_torsion_eff": -1.2e-4,
}


def load_reference() -> dict[str, object]:
    return {
        "source": "minimal theoretical bounds",
        "locked_names": list(FINAL_LOCKED_NAMES),
        "frozen_names": list(FINAL_FROZEN_NAMES),
        "order": list(REFERENCE_ORDER),
        "targets": dict(REFERENCE_TARGETS),
        "bounds": {name: list(bounds) for name, bounds in REFERENCE_BOUNDS.items()},
    }


def load_v16_prediction() -> dict[str, object]:
    return export_prediction()


def compare_prediction(v16_payload: dict[str, object] | None = None) -> dict[str, object]:
    payload = load_v16_prediction() if v16_payload is None else v16_payload
    external = payload["external"]

    rows: list[dict[str, object]] = []
    all_in_bounds = True
    all_signs_ok = True
    for name in REFERENCE_ORDER:
        predicted = float(external[name])
        target = float(REFERENCE_TARGETS[name])
        lower, upper = REFERENCE_BOUNDS[name]
        in_bounds = lower <= predicted <= upper
        midpoint = (lower + upper) / 2.0
        half_range = (upper - lower) / 2.0
        absolute_error = abs(predicted - target)
        relative_error = absolute_error / max(abs(target), 1.0e-12)
        center_offset = abs(predicted - midpoint) / max(half_range, 1.0e-12)
        sign_ok = predicted >= 0.0 if name != "grav_torsion_eff" else predicted <= 0.0
        rows.append(
            {
                "name": name,
                "predicted": predicted,
                "target": target,
                "lower": lower,
                "upper": upper,
                "absolute_error": absolute_error,
                "relative_error": relative_error,
                "center_offset": center_offset,
                "in_bounds": in_bounds,
                "sign_ok": sign_ok,
            }
        )
        all_in_bounds = all_in_bounds and in_bounds
        all_signs_ok = all_signs_ok and sign_ok

    comparison_ok = bool(payload.get("verdict") == "supported" and all_in_bounds and all_signs_ok)
    return {
        "v16": payload,
        "reference": load_reference(),
        "rows": rows,
        "all_in_bounds": all_in_bounds,
        "all_signs_ok": all_signs_ok,
        "comparison_ok": comparison_ok,
    }


def analyze_deviation(comparison: dict[str, object] | None = None) -> dict[str, object]:
    comparison_result = compare_prediction() if comparison is None else comparison
    rows = comparison_result["rows"]
    deviation_vector = {row["name"]: row["center_offset"] for row in rows}
    deviation_score = sum(deviation_vector.values()) / max(len(deviation_vector), 1)

    if comparison_result["all_in_bounds"] and comparison_result["all_signs_ok"] and deviation_score <= 0.25:
        deviation_class = "supported"
    elif comparison_result["all_in_bounds"] and comparison_result["all_signs_ok"] and deviation_score <= 0.5:
        deviation_class = "marginal"
    else:
        deviation_class = "falsified"

    monotone_ok = all(row["center_offset"] >= 0.0 for row in rows)
    return {
        "comparison": comparison_result,
        "deviation_vector": deviation_vector,
        "deviation_score": deviation_score,
        "deviation_class": deviation_class,
        "monotone_ok": monotone_ok,
    }


def evaluate_verdict(comparison: dict[str, object] | None = None) -> dict[str, object]:
    deviation = analyze_deviation(comparison)
    if deviation["deviation_class"] == "supported":
        verdict = "supported"
    elif deviation["deviation_class"] == "marginal":
        verdict = "marginal"
    else:
        verdict = "falsified"
    return {
        "comparison": deviation["comparison"],
        "deviation": deviation,
        "verdict": verdict,
    }


def v17_result_dir(output_dir: str | Path | None = None) -> Path:
    root = workspace_root()
    return Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")