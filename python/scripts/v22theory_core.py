"""Shared helpers for the V22 theory suite."""
from __future__ import annotations

import json
from pathlib import Path

from v13calibration_core import ALPHA_REF
from v19metacalibration_core import best_v18_profile, evaluate_sensitivity, v19_result_dir
from v20research_core import evaluate_geo, evaluate_hierarchy, evaluate_torsion
from v21borderline_core import evaluate_borderline


V22_SOURCE_MAP = {
    "constants": "NIST CODATA 2022",
    "spectroscopy": "NIST ASD",
    "astrophysics": ["SDSS DR17", "NED", "XMM-Newton"],
    "torsion": "arXiv:hep-th/0103093",
    "simulation": ["DLMF 34", "DLMF 34.2"],
}


def v22_reference_theta() -> dict[str, float]:
    best = best_v18_profile()
    return dict(best["theta_v18"])


def evaluate_geometry(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    geometry = evaluate_geo(theta)
    alpha0_value = float(theta["alpha0"])
    alpha_offset = alpha0_value - ALPHA_REF
    metric_form = {
        "g_int": {"alpha0": alpha0_value, "s_geo": float(theta["s_geo"]), "s_atom": float(theta["s_atom"])},
        "reference": "internal diagonal metric derived from V20 geometry",
    }
    alpha0_invariant_type = "dimensionless_invariant" if abs(alpha_offset) < 1.0e-4 else "dimensionless_shifted"
    curvature_state = "flat-locally-stable" if float(geometry["curvature_indicator"]) <= 1.0e-4 else "curved"
    geometry_model_ok = bool(geometry["verdict"] == "supported" and geometry["geostructureok"])

    return {
        "theta_reference": theta,
        "sources": [V22_SOURCE_MAP["constants"], V22_SOURCE_MAP["spectroscopy"], "SDSS DR17", "DLMF 34.2"],
        "alpha_CODATA": ALPHA_REF,
        "alpha_offset": alpha_offset,
        "delta_alpha_limit": 1.0e-4,
        "metric_formulation": metric_form,
        "alpha0invarianttype": alpha0_invariant_type,
        "curvature_state": curvature_state,
        "geometrymodelok": geometry_model_ok,
        "geometry_support": geometry,
        "verdict": "supported" if geometry_model_ok else "supported-partial" if geometry["verdict"] == "supported-partial" else "fragile",
    }


def evaluate_torsion_theory(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    torsion = evaluate_torsion(theta)
    borderline = evaluate_borderline(theta)
    torsion_connection_form = {
        "Gamma": "Levi-Civita + K(p, A_kappa)",
        "torsion_tensor": "K^lambda_{mu nu}(p, A_kappa)",
        "observable_anchor": "grav_torsion_eff",
    }
    torsion_invariant_type = "metric_affine_with_torsion"
    torsion_stability_state = "stable" if torsion["verdict"] == "supported" and borderline["verdict"] in {"supported", "supported-partial"} else "borderline"
    torsion_model_ok = bool(torsion["verdict"] == "supported" and torsion["torsion_stability"])

    return {
        "theta_reference": theta,
        "sources": [V22_SOURCE_MAP["torsion"], V22_SOURCE_MAP["spectroscopy"], "ESA XMM-Newton", "SDSS DR17"],
        "torsionconnectionform": torsion_connection_form,
        "torsioninvarianttype": torsion_invariant_type,
        "torsionstabilitystate": torsion_stability_state,
        "torsionmodelok": torsion_model_ok,
        "torsion_support": torsion,
        "borderline_support": borderline,
        "verdict": "supported" if torsion_model_ok else "supported-partial" if torsion["verdict"] == "supported-partial" else "fragile",
    }


def evaluate_hierarchy_theory(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    hierarchy = evaluate_hierarchy(theta)
    sensitivity = evaluate_sensitivity(theta)
    hierarchy_diagram = [
        {"parameter": "alpha0", "role": "invariant"},
        {"parameter": "s_geo", "role": "metric"},
        {"parameter": "s_atom", "role": "metric"},
        {"parameter": "p", "role": "torsion"},
        {"parameter": "A_kappa", "role": "coupling"},
    ]
    role_assignment = {entry["parameter"]: entry["role"] for entry in hierarchy_diagram}
    hierarchystabilitystate = "stable" if hierarchy["verdict"] == "supported" and sensitivity["top2_stable"] else "narrow"
    hierarchymodelok = bool(hierarchy["verdict"] == "supported" and sensitivity["top2_stable"])

    return {
        "theta_reference": theta,
        "sources": [V22_SOURCE_MAP["constants"], V22_SOURCE_MAP["spectroscopy"], "SDSS DR17", "DLMF 34.2"],
        "hierarchy_diagram": hierarchy_diagram,
        "role_assignment": role_assignment,
        "hierarchystabilitystate": hierarchystabilitystate,
        "hierarchymodelok": hierarchymodelok,
        "hierarchy_support": hierarchy,
        "sensitivity_support": sensitivity,
        "verdict": "supported" if hierarchymodelok else "supported-partial" if hierarchy["verdict"] == "supported-partial" else "fragile",
    }


def evaluate_v22_theory(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    geometry = evaluate_geometry(theta)
    torsion = evaluate_torsion_theory(theta)
    hierarchy = evaluate_hierarchy_theory(theta)

    coherent_theory = bool(geometry["geometrymodelok"] and torsion["torsionmodelok"] and hierarchy["hierarchymodelok"])
    if coherent_theory:
        theory_verdict = "coherent_theory"
        open_questions = []
    elif geometry["verdict"] == "supported-partial" or torsion["verdict"] == "supported-partial" or hierarchy["verdict"] == "supported-partial":
        theory_verdict = "partial_theory"
        open_questions = ["geometry", "torsion", "hierarchy"]
    else:
        theory_verdict = "inconclusive"
        open_questions = ["geometry", "torsion", "hierarchy", "sources"]

    theory_schema = {
        "geometry": geometry["metric_formulation"],
        "torsion": torsion["torsionconnectionform"],
        "hierarchy": hierarchy["hierarchy_diagram"],
    }
    key_invariants = {
        "alpha0": geometry["alpha_CODATA"],
        "curvature_state": geometry["curvature_state"],
        "torsion_state": torsion["torsionstabilitystate"],
        "hierarchy_state": hierarchy["hierarchystabilitystate"],
    }

    return {
        "theta_reference": theta,
        "V22_GEOMETRY": geometry,
        "V22_TORSION_THEORY": torsion,
        "V22_HIERARCHY_THEORY": hierarchy,
        "theory_verdict": theory_verdict,
        "theory_schema": theory_schema,
        "key_invariants": key_invariants,
        "open_questions": open_questions,
        "verdict": "supported" if coherent_theory else "supported-partial" if theory_verdict == "partial_theory" else "fragile",
    }


def v22_result_dir(output_dir: str | Path | None = None) -> Path:
    return Path(output_dir) if output_dir is not None else v19_result_dir()


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")