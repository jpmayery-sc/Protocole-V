"""Shared helpers for the V20 research suite."""
from __future__ import annotations

import json
import statistics
from pathlib import Path

from v15consolidation_core import consolidated_theta
from v16prediction_core import export_prediction, predict_internal, predict_external
from v19metacalibration_core import (
    MAP_OFFSETS,
    SENSITIVITY_STEPS,
    best_v18_profile,
    clamp_theta,
    evaluate_sensitivity,
    perturb_theta,
    v19_result_dir,
)


V20_GEO_AXES = ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
V20_SUPPORTED_VERDICTS = {"supported", "supported-partial"}


def v20_reference_theta() -> dict[str, float]:
    best = best_v18_profile()
    return dict(best["theta_v18"])


def center_prediction(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v20_reference_theta() if theta_reference is None else dict(theta_reference)
    prediction = export_prediction(theta)
    internal = prediction["internal"]
    external = prediction["external"]
    return {
        "theta_reference": theta,
        "prediction": prediction,
        "internal": internal,
        "external": external,
        "internal_balance": float(internal["internal_balance"]),
        "alpha_residual": float(internal["alpha_residual"]),
        "grav_torsion_eff": float(external["grav_torsion_eff"]),
    }


def _finite_difference(values_low: float, values_high: float, step: float) -> float:
    return (values_high - values_low) / (2.0 * step)


def evaluate_geo(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    center = center_prediction(theta_reference)
    theta = dict(center["theta_reference"])

    s_geo_step = SENSITIVITY_STEPS["s_geo"]
    s_atom_step = SENSITIVITY_STEPS["s_atom"]
    alpha0_step = SENSITIVITY_STEPS["alpha0"]

    geo_low = predict_internal(perturb_theta(theta, "s_geo", -s_geo_step))
    geo_high = predict_internal(perturb_theta(theta, "s_geo", s_geo_step))
    atom_low = predict_internal(perturb_theta(theta, "s_atom", -s_atom_step))
    atom_high = predict_internal(perturb_theta(theta, "s_atom", s_atom_step))
    alpha_low = export_prediction(perturb_theta(theta, "alpha0", -alpha0_step))["external"]
    alpha_high = export_prediction(perturb_theta(theta, "alpha0", alpha0_step))["external"]

    geo_gradient = _finite_difference(float(geo_low["z_geo"]), float(geo_high["z_geo"]), s_geo_step)
    atom_gradient = _finite_difference(float(atom_low["z_int"]), float(atom_high["z_int"]), s_atom_step)
    mod_geo_gradient = _finite_difference(float(geo_low["z_mod"]), float(geo_high["z_mod"]), s_geo_step)
    mod_atom_gradient = _finite_difference(float(atom_low["z_mod"]), float(atom_high["z_mod"]), s_atom_step)
    canal_gradient = _finite_difference(float(geo_low["z_canal"]), float(geo_high["z_canal"]), s_geo_step)
    alpha0_link = max(
        abs(float(alpha_high["grav_torsion_eff"]) - float(center["grav_torsion_eff"])) / alpha0_step,
        abs(float(center["grav_torsion_eff"]) - float(alpha_low["grav_torsion_eff"])) / alpha0_step,
    )

    cross_curvature = (
        float(atom_high["z_mod"])
        - float(geo_high["z_mod"])
        - float(atom_low["z_mod"])
        + float(geo_low["z_mod"])
    ) / max(4.0 * s_geo_step * s_atom_step, 1.0e-30)

    metric_consistency = (
        geo_gradient > 0.0
        and atom_gradient > 0.0
        and mod_geo_gradient > 0.0
        and mod_atom_gradient > 0.0
        and 0.25 <= geo_gradient / max(atom_gradient, 1.0e-30) <= 4.0
        and abs(float(center["internal_balance"])) <= 3.5e-06
    )
    geostructureok = metric_consistency and alpha0_link > 1.0e4
    curvature_indicator = abs(cross_curvature) + abs(mod_geo_gradient - mod_atom_gradient)

    if geostructureok and curvature_indicator <= 1.0e-4:
        verdict = "supported"
    elif geostructureok:
        verdict = "supported-partial"
    else:
        verdict = "fragile"

    return {
        "theta_reference": theta,
        "center": center,
        "geo_gradient": geo_gradient,
        "atom_gradient": atom_gradient,
        "mod_geo_gradient": mod_geo_gradient,
        "mod_atom_gradient": mod_atom_gradient,
        "canal_gradient": canal_gradient,
        "alpha0_geometriclink": alpha0_link,
        "curvature_indicator": curvature_indicator,
        "metric_consistency": metric_consistency,
        "geostructureok": geostructureok,
        "verdict": verdict,
    }


def evaluate_torsion(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    center = center_prediction(theta_reference)
    theta = dict(center["theta_reference"])

    p_step = SENSITIVITY_STEPS["p"]
    kappa_step = SENSITIVITY_STEPS["A_kappa"]
    p_low_prediction = export_prediction(perturb_theta(theta, "p", -p_step))
    p_high_prediction = export_prediction(perturb_theta(theta, "p", p_step))
    kappa_low_prediction = export_prediction(perturb_theta(theta, "A_kappa", -kappa_step))
    kappa_high_prediction = export_prediction(perturb_theta(theta, "A_kappa", kappa_step))
    p_low = p_low_prediction["external"]
    p_high = p_high_prediction["external"]
    kappa_low = kappa_low_prediction["external"]
    kappa_high = kappa_high_prediction["external"]
    kappa_low_internal = kappa_low_prediction["internal"]
    kappa_high_internal = kappa_high_prediction["internal"]

    torsion_strength = abs(float(center["grav_torsion_eff"]))
    torsion_p_derivative = _finite_difference(float(p_low["grav_torsion_eff"]), float(p_high["grav_torsion_eff"]), p_step)
    torsion_kappa_derivative = _finite_difference(float(kappa_low["grav_torsion_eff"]), float(kappa_high["grav_torsion_eff"]), kappa_step)
    canal_coupling = _finite_difference(float(kappa_low_internal["z_canal"]), float(kappa_high_internal["z_canal"]), kappa_step)
    torsion_variation = max(
        abs(float(p_high["grav_torsion_eff"]) - float(center["grav_torsion_eff"])),
        abs(float(p_low["grav_torsion_eff"]) - float(center["grav_torsion_eff"])),
        abs(float(kappa_high["grav_torsion_eff"]) - float(center["grav_torsion_eff"])),
        abs(float(kappa_low["grav_torsion_eff"]) - float(center["grav_torsion_eff"])),
    )
    torsion_stability = torsion_variation <= 1.0e-7 and torsion_strength > 0.0
    affine_signature = {
        "p": "positive" if torsion_p_derivative > 0.0 else "negative" if torsion_p_derivative < 0.0 else "neutral",
        "A_kappa": "positive" if torsion_kappa_derivative > 0.0 else "negative" if torsion_kappa_derivative < 0.0 else "neutral",
        "canal": "positive" if canal_coupling > 0.0 else "negative" if canal_coupling < 0.0 else "neutral",
    }
    torsion_kappa_coupling = abs(torsion_kappa_derivative)

    if torsion_stability and torsion_kappa_coupling > 0.0 and abs(torsion_p_derivative) > 0.0:
        verdict = "supported"
    elif torsion_strength > 0.0 and (abs(torsion_p_derivative) > 0.0 or torsion_kappa_coupling > 0.0):
        verdict = "supported-partial"
    else:
        verdict = "fragile"

    return {
        "theta_reference": theta,
        "center": center,
        "torsion_strength": torsion_strength,
        "torsion_p_derivative": torsion_p_derivative,
        "torsion_kappa_coupling": torsion_kappa_coupling,
        "torsion_stability": torsion_stability,
        "affine_signature": affine_signature,
        "canal_coupling": canal_coupling,
        "verdict": verdict,
    }


def evaluate_hierarchy(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    sensitivity = evaluate_sensitivity(v20_reference_theta() if theta_reference is None else theta_reference)
    ranking = list(sensitivity["ranking"])
    hierarchy_ranking = [
        {
            "parameter": row["parameter"],
            "weight": row["abs_derivative"],
            "role": "metric" if row["parameter"] in {"s_geo", "s_atom"} else "torsion" if row["parameter"] == "p" else "coupling" if row["parameter"] == "A_kappa" else "anchor",
        }
        for row in ranking
    ]
    dominant_parameter = hierarchy_ranking[0]["parameter"] if hierarchy_ranking else "unknown"
    metric_parameters = [entry["parameter"] for entry in hierarchy_ranking if entry["parameter"] in {"s_geo", "s_atom"}]
    torsion_parameter = "p"
    coupling_parameter = "A_kappa"
    stable_hierarchy = sensitivity["top2_stable"] and sensitivity["dominant_gap"] >= 1.2 and dominant_parameter in {"alpha0", "A_kappa", "p"}

    if stable_hierarchy and len(metric_parameters) == 2:
        verdict = "supported"
    elif stable_hierarchy:
        verdict = "supported-partial"
    else:
        verdict = "fragile"

    return {
        "theta_reference": dict(v20_reference_theta() if theta_reference is None else theta_reference),
        "sensitivity": sensitivity,
        "hierarchy_ranking": hierarchy_ranking,
        "dominant_parameter": dominant_parameter,
        "metric_parameters": metric_parameters,
        "torsion_parameter": torsion_parameter,
        "coupling_parameter": coupling_parameter,
        "stable_hierarchy": stable_hierarchy,
        "verdict": verdict,
    }


def evaluate_v20_verdict(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    geo = evaluate_geo(theta_reference)
    torsion = evaluate_torsion(theta_reference)
    hierarchy = evaluate_hierarchy(theta_reference)

    supported_count = sum(1 for verdict in [geo["verdict"], torsion["verdict"], hierarchy["verdict"]] if verdict == "supported")
    partial_count = sum(1 for verdict in [geo["verdict"], torsion["verdict"], hierarchy["verdict"]] if verdict == "supported-partial")

    if geo["verdict"] == "supported" and torsion["verdict"] == "supported" and hierarchy["verdict"] == "supported":
        verdict_global = "supported"
        structure_detectee = "coherente"
        niveau_de_confiance = "haute"
    elif supported_count == 2 and partial_count == 1:
        verdict_global = "supported-partial"
        structure_detectee = "emergente"
        niveau_de_confiance = "moyenne"
    elif geo["verdict"] == "fragile" or torsion["verdict"] == "fragile" or hierarchy["verdict"] == "fragile":
        verdict_global = "fragile"
        structure_detectee = "fragile"
        niveau_de_confiance = "faible"
    else:
        verdict_global = "supported-partial"
        structure_detectee = "emergente"
        niveau_de_confiance = "moyenne"

    module_scores = {
        "v20_geo": geo,
        "v20_torsion": torsion,
        "v20_hierarchy": hierarchy,
    }
    worst_module = min(module_scores.items(), key=lambda item: (0 if item[1]["verdict"] == "supported" else 1 if item[1]["verdict"] == "supported-partial" else 2, item[0]))[0]

    if verdict_global == "supported":
        zone_recherche_prioritaire = "v21-theory"
    elif verdict_global == "supported-partial":
        zone_recherche_prioritaire = worst_module
    else:
        zone_recherche_prioritaire = worst_module

    return {
        "v20_geo": geo,
        "v20_torsion": torsion,
        "v20_hierarchy": hierarchy,
        "verdict_global": verdict_global,
        "structure_detectee": structure_detectee,
        "niveau_de_confiance": niveau_de_confiance,
        "zone_de_recherche_prioritaire": zone_recherche_prioritaire,
        "verdict": verdict_global,
    }


def v20_result_dir(output_dir: str | Path | None = None) -> Path:
    return Path(output_dir) if output_dir is not None else v19_result_dir()


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")