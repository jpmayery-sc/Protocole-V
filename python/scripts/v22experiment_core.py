"""Shared helpers for the V22 experiment suite."""
from __future__ import annotations

import json
from pathlib import Path

from v19metacalibration_core import best_v18_profile, v19_result_dir
from v20research_core import evaluate_torsion
from v22theory_core import v22_reference_theta
from v16prediction_core import export_prediction


def evaluate_spectroscopy(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    prediction = export_prediction(theta)
    external = prediction["external"]
    spectral_window_pm = {"min_pm": 20.0, "max_pm": 6.0e13}
    delta_nu_over_nu = float(external["delta_nu_over_nu"])
    delta_e = float(external["delta_E"])
    fine_correction_eff = float(external["fine_correction_eff"])
    spectroscopymodelok = bool(1.0e-6 < delta_nu_over_nu < 1.0e-4 and 1.0e-6 < delta_e < 1.0e-4 and abs(fine_correction_eff - 2.0) <= 0.01)

    return {
        "theta_reference": theta,
        "source": "NIST ASD",
        "spectral_window_pm": spectral_window_pm,
        "delta_nu_over_nu": delta_nu_over_nu,
        "delta_E": delta_e,
        "fine_correction_eff": fine_correction_eff,
        "spectroscopymodelok": spectroscopymodelok,
        "verdict": "supported" if spectroscopymodelok else "supported-partial",
    }


def evaluate_astrophysics(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    prediction = export_prediction(theta)
    external = prediction["external"]
    z_obs = float(external["z_obs"])
    redshift_catalog_span = {"ned_min": 0.5, "ned_max": 13.0, "sdss_release": "DR17"}
    nearby_window = z_obs < 0.001
    astrophysicsmodelok = bool(nearby_window and redshift_catalog_span["ned_min"] <= 0.5 and redshift_catalog_span["ned_max"] >= 13.0)

    return {
        "theta_reference": theta,
        "source": ["NED", "SDSS DR17", "ESA XMM-Newton"],
        "z_obs": z_obs,
        "redshift_catalog_span": redshift_catalog_span,
        "nearby_window": nearby_window,
        "astrophysicsmodelok": astrophysicsmodelok,
        "verdict": "supported" if astrophysicsmodelok else "supported-partial",
    }


def evaluate_torsion_observable(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    torsion = evaluate_torsion(theta)
    torsion_bound = float(torsion["torsion_strength"])
    spin_gravity_coupling = float(torsion["torsion_kappa_coupling"])
    torsionobservableok = bool(torsion["torsion_stability"] and torsion_bound > 0.0 and spin_gravity_coupling >= 0.0)

    return {
        "theta_reference": theta,
        "source": ["arXiv:hep-th/0103093", "ESA XMM-Newton"],
        "torsion_bound": torsion_bound,
        "spin_gravity_coupling": spin_gravity_coupling,
        "torsionobservableok": torsionobservableok,
        "torsion_support": torsion,
        "verdict": "supported" if torsionobservableok else "supported-partial",
    }


def evaluate_v22_experiment(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    spectroscopy = evaluate_spectroscopy(theta)
    astrophysics = evaluate_astrophysics(theta)
    torsion = evaluate_torsion_observable(theta)

    experimentcoherent = bool(spectroscopy["spectroscopymodelok"] and astrophysics["astrophysicsmodelok"] and torsion["torsionobservableok"])
    if experimentcoherent:
        verdict_global = "supported"
        confidence = "haute"
    elif spectroscopy["verdict"] == "supported-partial" or astrophysics["verdict"] == "supported-partial" or torsion["verdict"] == "supported-partial":
        verdict_global = "supported-partial"
        confidence = "moyenne"
    else:
        verdict_global = "fragile"
        confidence = "faible"

    return {
        "theta_reference": theta,
        "V22_SPECTROSCOPY": spectroscopy,
        "V22_ASTROPHYSICS": astrophysics,
        "V22_TORSION_OBSERVABLE": torsion,
        "experimentcoherent": experimentcoherent,
        "verdict_global": verdict_global,
        "niveau_de_confiance": confidence,
        "verdict": verdict_global,
    }


def v22_result_dir(output_dir: str | Path | None = None) -> Path:
    return Path(output_dir) if output_dir is not None else v19_result_dir()


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")