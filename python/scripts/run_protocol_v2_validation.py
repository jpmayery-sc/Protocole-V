"""Run the transport V2 validation on the real HF transport datasets.

The repository now contains normalized skin-depth tables for Cu, Al, Ag, and
Fe. This validator treats the per-material amplitude

    A = delta(f) * sqrt(f)

as the sufficient statistic for the shared f^-1/2 transport law, then checks
whether progressively richer corrections improve the cross-material transfer.

Operationally:
- H1: constant amplitude only.
- H2: global alpha' correction against a conductivity proxy.
- H3: quadratic beta' correction for the nonlinear Fe branch.
- H4: mass-weighted FTM comparison using sigma * sqrt(m) * K(omega).

The report is intentionally honest about whether each stage actually improves
transfer on these published datasets.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path
from typing import Iterable


ASSUMED_FRACTIONAL_UNCERTAINTY = 0.01
NONLINEAR_MATERIAL = "fe"

ATOMIC_MASS_AMU = {
    "cu": 63.546,
    "al": 26.9815385,
    "ag": 107.8682,
    "fe": 55.845,
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_manifest(root: Path) -> dict:
    manifest_path = root / "python" / "data" / "hf_transport_manifest.json"
    return load_json(manifest_path)


def dataset_path(root: Path, entry: dict) -> Path:
    relative_path = entry.get("file") or entry.get("path")
    if not relative_path:
        raise ValueError("Dataset entry is missing a file path")
    return root / relative_path.replace("/", "\\")


def mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / len(values)


def rmse(errors: Iterable[float]) -> float:
    errors = list(errors)
    return math.sqrt(sum(error * error for error in errors) / len(errors))


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]

    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row_index: abs(augmented[row_index][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) < 1.0e-15:
            raise ValueError("Singular linear system")
        if pivot_row != pivot_index:
            augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]

        pivot = augmented[pivot_index][pivot_index]
        for column_index in range(pivot_index, size + 1):
            augmented[pivot_index][column_index] /= pivot

        for row_index in range(size):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            if factor == 0.0:
                continue
            for column_index in range(pivot_index, size + 1):
                augmented[row_index][column_index] -= factor * augmented[pivot_index][column_index]

    return [augmented[row_index][size] for row_index in range(size)]


def weighted_least_squares(features: list[list[float]], targets: list[float], weights: list[float] | None = None) -> list[float]:
    if weights is None:
        weights = [1.0] * len(targets)

    dimension = len(features[0])
    xtwx = [[0.0 for _ in range(dimension)] for _ in range(dimension)]
    xtwy = [0.0 for _ in range(dimension)]

    for row, target, weight in zip(features, targets, weights):
        for i in range(dimension):
            xtwy[i] += weight * row[i] * target
            for j in range(dimension):
                xtwx[i][j] += weight * row[i] * row[j]

    return solve_linear_system(xtwx, xtwy)


def predict(coefficients: list[float], feature_row: list[float]) -> float:
    return sum(coefficient * feature for coefficient, feature in zip(coefficients, feature_row))


def information_criteria(residuals: list[float], parameter_count: int, sigma: float = 1.0) -> tuple[float, float, float]:
    n = len(residuals)
    sse = sum(error * error for error in residuals)
    if sse <= 0.0:
        sse = 1.0e-24
    variance = max((sse / n) / (sigma * sigma), 1.0e-24)
    chi2 = sse / (sigma * sigma)
    chi2_reduced = chi2 / max(n - parameter_count, 1)
    aic = n * math.log(variance) + 2.0 * parameter_count
    bic = n * math.log(variance) + parameter_count * math.log(n)
    return chi2_reduced, aic, bic


def material_amplitude(records: list[dict]) -> float:
    amplitudes = [record["skin_depth_m"] * math.sqrt(record["frequency_hz"]) for record in records]
    return statistics.median(amplitudes)


def load_material_series(root: Path) -> list[dict]:
    manifest = load_manifest(root)
    datasets = manifest.get("datasets", {})
    materials: list[dict] = []

    for label, entry in datasets.items():
        path = dataset_path(root, entry)
        dataset = load_json(path)
        method = dataset.get("method", {})
        assumptions = method.get("assumptions", {})
        rho = float(assumptions.get("rho_ohm_m"))
        mu_r = float(assumptions.get("mu_r_eff", 1.0))
        records = dataset.get("records", [])
        if not records:
            raise ValueError(f"Dataset {label} has no records")

        amplitudes = [record["skin_depth_m"] * math.sqrt(record["frequency_hz"]) for record in records]
        materials.append(
            {
                "label": label,
                "path": str(path.relative_to(root)),
                "rho_ohm_m": rho,
                "mu_r_eff": mu_r,
                "conductivity_proxy": 1.0 / rho,
                "mass_amu": ATOMIC_MASS_AMU[label],
                "records": records,
                "amplitude_obs": statistics.median(amplitudes),
                "amplitude_mean": mean(amplitudes),
                "amplitude_cv": statistics.stdev(amplitudes) / max(statistics.mean(amplitudes), 1.0e-24) if len(amplitudes) > 1 else 0.0,
            }
        )

    return materials


def fit_model(materials: list[dict], degree: int, weighted: bool = False) -> tuple[list[float], float]:
    x_values = [math.log10(material["conductivity_proxy"]) for material in materials]
    x_center = mean(x_values)
    features: list[list[float]] = []
    targets: list[float] = []
    weights: list[float] = []

    for material, x_value in zip(materials, x_values):
        x = x_value - x_center
        row = [1.0]
        if degree >= 1:
            row.append(x)
        if degree >= 2:
            row.append(x * x)
        features.append(row)
        targets.append(material["amplitude_obs"])
        weights.append(math.sqrt(material["mass_amu"]) if weighted else 1.0)

    return weighted_least_squares(features, targets, weights), x_center


def model_predict(coefficients: list[float], x_center: float, material: dict) -> float:
    x = math.log10(material["conductivity_proxy"]) - x_center
    if len(coefficients) == 1:
        return predict(coefficients, [1.0])
    if len(coefficients) == 2:
        return predict(coefficients, [1.0, x])
    return predict(coefficients, [1.0, x, x * x])


def evaluate_fold(held_out_index: int, materials: list[dict], degree: int, weighted: bool = False) -> dict:
    train_materials = [material for index, material in enumerate(materials) if index != held_out_index]
    held_out = materials[held_out_index]
    coefficients, x_center = fit_model(train_materials, degree=degree, weighted=weighted)
    amplitude_prediction = model_predict(coefficients, x_center, held_out)

    predictions = [amplitude_prediction / math.sqrt(record["frequency_hz"]) for record in held_out["records"]]
    observed = [record["skin_depth_m"] for record in held_out["records"]]
    residuals = [predicted - actual for predicted, actual in zip(predictions, observed)]
    relative_errors = [abs(residual) / max(actual, 1.0e-24) for residual, actual in zip(residuals, observed)]
    sigma = [max(abs(actual) * ASSUMED_FRACTIONAL_UNCERTAINTY, 1.0e-12) for actual in observed]
    chi2 = sum((residual / sigma_value) ** 2 for residual, sigma_value in zip(residuals, sigma))
    dof = max(len(residuals) - len(coefficients), 1)
    chi2_reduced = chi2 / dof
    sse = sum(residual * residual for residual in residuals)
    variance = max(sse / len(residuals), 1.0e-24)
    aic = len(residuals) * math.log(variance) + 2.0 * len(coefficients)
    bic = len(residuals) * math.log(variance) + len(coefficients) * math.log(len(residuals))

    return {
        "material": held_out["label"],
        "coefficients": coefficients,
        "x_center": x_center,
        "amplitude_prediction": amplitude_prediction,
        "amplitude_observed": held_out["amplitude_obs"],
        "rmse": rmse(residuals),
        "mean_relative_error": mean(relative_errors),
        "max_relative_error": max(relative_errors),
        "chi2_reduced": chi2_reduced,
        "aic": aic,
        "bic": bic,
        "residuals": residuals,
        "observed": observed,
        "predictions": predictions,
    }


def evaluate_model(materials: list[dict], degree: int, weighted: bool = False) -> dict:
    folds = [evaluate_fold(index, materials, degree=degree, weighted=weighted) for index in range(len(materials))]
    all_residuals = [residual for fold in folds for residual in fold["residuals"]]
    all_observed = [actual for fold in folds for actual in fold["observed"]]
    all_relative = [abs(residual) / max(actual, 1.0e-24) for fold in folds for residual, actual in zip(fold["residuals"], fold["observed"])]
    parameter_count = degree + 1
    chi2_reduced, aic, bic = information_criteria(all_residuals, parameter_count)

    return {
        "folds": folds,
        "overall_rmse": rmse(all_residuals),
        "mean_relative_error": mean(all_relative),
        "max_relative_error": max(all_relative),
        "chi2_reduced": chi2_reduced,
        "aic": aic,
        "bic": bic,
        "observed_mean": mean(all_observed),
        "parameter_count": parameter_count,
    }


def amplitude_spread(values: list[float]) -> dict:
    spread = statistics.stdev(values) if len(values) > 1 else 0.0
    avg = statistics.mean(values)
    cv = spread / max(abs(avg), 1.0e-24)
    return {"mean": avg, "stdev": spread, "cv": cv}


def build_summary(materials: list[dict], result_dir: Path) -> dict:
    baseline = evaluate_model(materials, degree=0)
    alpha = evaluate_model(materials, degree=1)
    beta = evaluate_model(materials, degree=2)

    raw_amplitudes = [material["amplitude_obs"] for material in materials]
    mass_weighted_ftm = [material["amplitude_obs"] * material["conductivity_proxy"] * math.sqrt(material["mass_amu"]) for material in materials]
    raw_spread = amplitude_spread(raw_amplitudes)
    weighted_spread = amplitude_spread(mass_weighted_ftm)

    h1_supported = baseline["mean_relative_error"] > 0.15 or baseline["overall_rmse"] > 0.02
    h2_supported = alpha["overall_rmse"] < baseline["overall_rmse"] * 0.8 and alpha["mean_relative_error"] < baseline["mean_relative_error"]
    h3_supported = beta["overall_rmse"] < alpha["overall_rmse"] * 0.9 and beta["mean_relative_error"] <= alpha["mean_relative_error"]
    h4_supported = weighted_spread["cv"] < raw_spread["cv"]

    stages = [
        {
            "id": "H1",
            "title": "Local model only",
            "verdict": "supported" if h1_supported else "contradicted",
            "reason": "A single amplitude term does not transfer cleanly across Cu, Al, Ag, and Fe." if h1_supported else "The local amplitude model transferred better than expected.",
            "metrics": baseline,
        },
        {
            "id": "H2",
            "title": "Global alpha' correction",
            "verdict": "supported" if h2_supported else "contradicted",
            "reason": "The conductivity-proxy correction reduces cross-material error by at least 20%." if h2_supported else "The alpha' correction does not improve transfer enough.",
            "metrics": alpha,
        },
        {
            "id": "H3",
            "title": "Quadratic beta' term",
            "verdict": "supported" if h3_supported else "contradicted",
            "reason": "The quadratic term improves the cross-validated fit beyond the linear alpha' model." if h3_supported else "The quadratic term is not justified by the held-out error.",
            "metrics": beta,
        },
        {
            "id": "H4",
            "title": "Mass-weighted FTM comparison",
            "verdict": "supported" if h4_supported else "contradicted",
            "reason": "sigma * sqrt(m) lowers the cross-material coefficient of variation." if h4_supported else "The mass-weighted transform increases the spread across materials.",
            "metrics": {
                "raw_spread": raw_spread,
                "mass_weighted_spread": weighted_spread,
            },
        },
    ]

    supported_count = sum(1 for stage in stages if stage["verdict"] == "supported")
    if supported_count == len(stages):
        overall_verdict = "supported"
    elif supported_count == 0:
        overall_verdict = "contradicted"
    else:
        overall_verdict = "partiel"

    summary = {
        "suite": "protocol_v2_validation",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": supported_count,
        "total": len(stages),
        "stages": stages,
        "baseline": baseline,
        "alpha": alpha,
        "beta": beta,
        "raw_spread": raw_spread,
        "mass_weighted_spread": weighted_spread,
        "materials": [
            {
                "label": material["label"],
                "rho_ohm_m": material["rho_ohm_m"],
                "mu_r_eff": material["mu_r_eff"],
                "conductivity_proxy": material["conductivity_proxy"],
                "mass_amu": material["mass_amu"],
                "amplitude_obs": material["amplitude_obs"],
                "path": material["path"],
            }
            for material in materials
        ],
    }

    json_path = result_dir / f"protocol_v2_validation_summary_{summary['timestamp']}.json"
    txt_path = result_dir / f"protocol_v2_validation_summary_{summary['timestamp']}.txt"
    md_path = result_dir / "protocole_v2_validation.md"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path), "md_path": str(md_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Protocol V2 validation summary",
        f"timestamp: {summary['timestamp']}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        "",
        "Stages:",
    ]
    for stage in stages:
        lines.append(f"- {stage['id']}: {stage['verdict']} - {stage['title']}")
        lines.append(f"  - {stage['reason']}")
        if stage["id"] == "H4":
            lines.append(f"  - raw_cv: {raw_spread['cv']:.6f}")
            lines.append(f"  - weighted_cv: {weighted_spread['cv']:.6f}")
    lines.extend([
        "",
        "Model metrics:",
        f"- H1 RMSE: {baseline['overall_rmse']:.6f}",
        f"- H1 mean relative error: {baseline['mean_relative_error']:.6f}",
        f"- H2 RMSE: {alpha['overall_rmse']:.6f}",
        f"- H2 mean relative error: {alpha['mean_relative_error']:.6f}",
        f"- H3 RMSE: {beta['overall_rmse']:.6f}",
        f"- H3 mean relative error: {beta['mean_relative_error']:.6f}",
        f"- H4 raw CV: {raw_spread['cv']:.6f}",
        f"- H4 weighted CV: {weighted_spread['cv']:.6f}",
    ])
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    md_lines = [
        "# Protocole V2 - Validation numerique",
        "",
        "## But",
        "Valider les etages H1 a H4 sur les jeux HF reels normalises.",
        "",
        "## Verdict",
        f"- Verdict global: {summary['overall_verdict']}",
        f"- Statut des donnees: ready",
        f"- Jeux utilises: {', '.join(material['label'].upper() for material in materials)}",
        "",
        "## Etages",
    ]
    for stage in stages:
        md_lines.append(f"- {stage['id']}: {stage['verdict']} - {stage['title']}")
        md_lines.append(f"  - {stage['reason']}")
    md_lines.extend([
        "",
        "## Materiaux",
    ])
    for material in materials:
        md_lines.append(
            f"- {material['label'].upper()}: rho={material['rho_ohm_m']:.3e} mu_r={material['mu_r_eff']:.1f} amplitude={material['amplitude_obs']:.6f}"
        )
    md_lines.extend([
        "",
        "## Metriques",
        f"- H1 RMSE: {baseline['overall_rmse']:.6f}",
        f"- H1 erreur relative moyenne: {baseline['mean_relative_error']:.6f}",
        f"- H2 RMSE: {alpha['overall_rmse']:.6f}",
        f"- H2 erreur relative moyenne: {alpha['mean_relative_error']:.6f}",
        f"- H3 RMSE: {beta['overall_rmse']:.6f}",
        f"- H3 erreur relative moyenne: {beta['mean_relative_error']:.6f}",
        f"- H4 CV brut: {raw_spread['cv']:.6f}",
        f"- H4 CV pondere: {weighted_spread['cv']:.6f}",
        "",
        "## Lecture courte",
        "Le validateur teste un modele d'amplitude commune A = delta * sqrt(f), puis des corrections globales sur le proxy de conductivite et une ponderation masse sigma * sqrt(m).",
        "",
        "Les fichiers sources utilises sont les jeux HF normalises du manifeste de travail.",
    ])
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    summary["md_path"] = str(md_path)
    return summary


def run_validation(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    result_dir.mkdir(parents=True, exist_ok=True)
    materials = load_material_series(root)
    return build_summary(materials, result_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the transport V2 validation on the real HF datasets.")
    parser.add_argument("--output-dir", default=None, help="Directory for the validation reports")
    args = parser.parse_args()

    result = run_validation(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()