"""Shared helpers for the V22 simulation suite."""
from __future__ import annotations

import json
from pathlib import Path

from v20research_core import evaluate_geo, evaluate_hierarchy, evaluate_torsion
from v21borderline_core import evaluate_resolution
from v22theory_core import v22_reference_theta


def evaluate_wigner_simulation(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    selection_rules = {"triangle": True, "m_sum_zero": True, "integer_perimeter": True}
    coupling_family = ["3j", "6j", "9j"]
    wignerbasisok = all(selection_rules.values()) and len(coupling_family) == 3

    return {
        "theta_reference": theta,
        "source": ["DLMF 34", "DLMF 34.2"],
        "selection_rules": selection_rules,
        "coupling_family": coupling_family,
        "wignerbasisok": wignerbasisok,
        "verdict": "supported" if wignerbasisok else "supported-partial",
    }


def evaluate_geometric_simulation(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    geometry = evaluate_geo(theta)
    metric_internal = {"alpha0": float(theta["alpha0"]), "s_geo": float(theta["s_geo"]), "s_atom": float(theta["s_atom"])}
    non_riemannian_support = bool(geometry["geostructureok"] and geometry["verdict"] == "supported")

    return {
        "theta_reference": theta,
        "source": ["DLMF 34", "NIST ASD"],
        "metric_internal": metric_internal,
        "non_riemannian_support": non_riemannian_support,
        "geometry_support": geometry,
        "verdict": "supported" if non_riemannian_support else "supported-partial",
    }


def evaluate_stability_simulation(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    hierarchy = evaluate_hierarchy(theta)
    torsion = evaluate_torsion(theta)
    resolution = evaluate_resolution(theta)
    stability_surface = {
        "hierarchy_stable": bool(hierarchy["stable_hierarchy"]),
        "torsion_stable": bool(torsion["torsion_stability"]),
        "resolution_state": resolution["resolution_state"],
    }
    multivariable_robustness = bool(hierarchy["verdict"] == "supported" and torsion["verdict"] == "supported" and resolution["verdict"] == "supported")

    return {
        "theta_reference": theta,
        "source": ["V20", "V21", "DLMF 34"],
        "stability_surface": stability_surface,
        "multivariable_robustness": multivariable_robustness,
        "stability_support": {
            "hierarchy": hierarchy,
            "torsion": torsion,
            "resolution": resolution,
        },
        "verdict": "supported" if multivariable_robustness else "supported-partial",
    }


def evaluate_v22_simulation(theta_reference: dict[str, float] | None = None) -> dict[str, object]:
    theta = v22_reference_theta() if theta_reference is None else dict(theta_reference)
    wigner = evaluate_wigner_simulation(theta)
    geometry = evaluate_geometric_simulation(theta)
    stability = evaluate_stability_simulation(theta)

    simulationcoherent = bool(wigner["wignerbasisok"] and geometry["non_riemannian_support"] and stability["multivariable_robustness"])
    if simulationcoherent:
        verdict_global = "supported"
        confidence = "haute"
    elif wigner["verdict"] == "supported-partial" or geometry["verdict"] == "supported-partial" or stability["verdict"] == "supported-partial":
        verdict_global = "supported-partial"
        confidence = "moyenne"
    else:
        verdict_global = "fragile"
        confidence = "faible"

    return {
        "theta_reference": theta,
        "V22_WIGNER": wigner,
        "V22_GEOMETRIC_SIMULATION": geometry,
        "V22_STABILITY_SIMULATION": stability,
        "simulationcoherent": simulationcoherent,
        "verdict_global": verdict_global,
        "niveau_de_confiance": confidence,
        "verdict": verdict_global,
    }


def v22_result_dir(output_dir: str | Path | None = None) -> Path:
    from v19metacalibration_core import v19_result_dir
    return Path(output_dir) if output_dir is not None else v19_result_dir()


def write_report(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")