"""Shared helpers for the V16 prediction suite."""
from __future__ import annotations

import json
import math
from pathlib import Path

from v13calibration_core import observable_model, theta_is_supported, workspace_root as v13_workspace_root
from v15consolidation_core import FINAL_FROZEN_NAMES, FINAL_LOCKED_NAMES, final_locked_theta, final_frozen_theta, workspace_root


INTERNAL_KEYS = ["z_geo", "z_int", "z_canal", "z_mod", "fine_delta", "alpha_residual"]
EXTERNAL_KEYS = ["z_obs", "delta_nu_over_nu", "delta_E", "fine_correction_eff", "grav_torsion_eff"]


def consolidated_theta() -> dict[str, float]:
    theta = final_frozen_theta()
    theta.update(final_locked_theta())
    return theta


def predict_internal(theta_v15: dict[str, float] | None = None) -> dict[str, float | dict[str, float]]:
    theta = consolidated_theta() if theta_v15 is None else dict(theta_v15)
    observables = observable_model(theta)
    internal = {key: observables[key] for key in INTERNAL_KEYS}
    internal["theta_v15"] = theta
    internal["theta_supported"] = theta_is_supported(theta)
    internal["internal_balance"] = internal["z_mod"] - (internal["z_geo"] + internal["z_int"] + internal["z_canal"]) / 3.0
    return internal


def predict_external(internal: dict[str, float | dict[str, float]]) -> dict[str, float]:
    z_mod = float(internal["z_mod"])
    fine_delta = float(internal["fine_delta"])
    alpha_residual = float(internal["alpha_residual"])
    z_obs = z_mod + 0.5 * fine_delta
    delta_nu_over_nu = z_mod + 0.1 * fine_delta
    delta_e = z_mod * 1.0e-3 + fine_delta * 1.0e-1
    fine_correction_eff = 1.0 + fine_delta / 0.00024
    grav_torsion_eff = (z_mod - z_obs) + alpha_residual * 1.0e6
    return {
        "z_obs": z_obs,
        "delta_nu_over_nu": delta_nu_over_nu,
        "delta_E": delta_e,
        "fine_correction_eff": fine_correction_eff,
        "grav_torsion_eff": grav_torsion_eff,
    }


def evaluate_consistency(theta_v15: dict[str, float] | None = None) -> dict[str, object]:
    internal = predict_internal(theta_v15)
    external = predict_external(internal)
    z_mod = float(internal["z_mod"])
    z_obs = external["z_obs"]
    delta_nu_over_nu = external["delta_nu_over_nu"]
    delta_e = external["delta_E"]

    internal_ok = (
        internal["theta_supported"]
        and float(internal["alpha_residual"]) < 1.0e-8
        and float(internal["z_geo"]) > 0.0
        and float(internal["z_int"]) > 0.0
        and float(internal["z_canal"]) > 0.0
        and float(internal["z_mod"]) > 0.0
    )
    external_ok = (
        z_obs > z_mod
        and delta_nu_over_nu > z_mod
        and delta_e > 0.0
        and external["fine_correction_eff"] >= 1.0
        and abs(external["grav_torsion_eff"]) < 1.0e-3
    )
    consistency_ok = math.isclose(z_obs - z_mod, 0.5 * float(internal["fine_delta"]), rel_tol=0.0, abs_tol=1.0e-15)
    verdict = "supported" if internal_ok and external_ok and consistency_ok else "falsified"
    return {
        "internal": internal,
        "external": external,
        "internal_ok": internal_ok,
        "external_ok": external_ok,
        "consistency_ok": consistency_ok,
        "verdict": verdict,
    }


def export_prediction(theta_v15: dict[str, float] | None = None) -> dict[str, object]:
    evaluation = evaluate_consistency(theta_v15)
    payload = {
        "suite": "v16prediction_suite",
        "locked_names": list(FINAL_LOCKED_NAMES),
        "frozen_names": list(FINAL_FROZEN_NAMES),
        "internal": evaluation["internal"],
        "external": evaluation["external"],
        "verdict": evaluation["verdict"],
    }
    return payload


def result_dir(output_dir: str | Path | None = None) -> Path:
    root = workspace_root()
    return Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")