"""Compare the prepared V29 test 1 datasets against a flat LCDM reference."""

from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import numpy as np

from v29finaltheory_core import v29_result_dir, write_report


SPEED_OF_LIGHT_KM_S = 299792.458
H0_REF = 67.4
OMEGA_M_REF = 0.315
RS_REF_MPC = 147.09


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def prepared_data_dir() -> Path:
    return workspace_root() / "results" / "result-analyse" / "v29_test1_data" / "prepared"


def flat_lcdm_e(z: np.ndarray, omega_m: float = OMEGA_M_REF) -> np.ndarray:
    return np.sqrt(omega_m * (1.0 + z) ** 3 + (1.0 - omega_m))


def prepare_distance_grid(z_max: float, grid_size: int | None = None) -> tuple[np.ndarray, np.ndarray]:
    size = grid_size or max(4096, int(math.ceil(z_max * 4000)) + 1)
    grid = np.linspace(0.0, z_max, size)
    inverse_e = 1.0 / flat_lcdm_e(grid)
    cumulative = np.zeros_like(grid)
    if grid.size > 1:
        dz = np.diff(grid)
        cumulative[1:] = np.cumsum(0.5 * (inverse_e[1:] + inverse_e[:-1]) * dz)
    return grid, cumulative


def comoving_distance(z: np.ndarray, h0: float = H0_REF, omega_m: float = OMEGA_M_REF) -> np.ndarray:
    if np.any(z < 0):
        raise ValueError("Redshift values must be non-negative")

    z_max = float(np.max(z)) if z.size else 0.0
    grid, integral = prepare_distance_grid(z_max)
    integral_at_z = np.interp(z, grid, integral)
    return (SPEED_OF_LIGHT_KM_S / h0) * integral_at_z


def luminosity_distance(z: np.ndarray, h0: float = H0_REF, omega_m: float = OMEGA_M_REF) -> np.ndarray:
    return (1.0 + z) * comoving_distance(z, h0=h0, omega_m=omega_m)


def distance_modulus(z: np.ndarray, h0: float = H0_REF, omega_m: float = OMEGA_M_REF) -> np.ndarray:
    return 5.0 * np.log10(luminosity_distance(z, h0=h0, omega_m=omega_m)) + 25.0


def hubble_parameter(z: np.ndarray, h0: float = H0_REF, omega_m: float = OMEGA_M_REF) -> np.ndarray:
    return h0 * flat_lcdm_e(z, omega_m=omega_m)


def load_chronometers(path: Path) -> list[dict[str, float]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, float]] = []
        for row in reader:
            rows.append(
                {
                    "z": float(row["z"]),
                    "Hz_km_s_Mpc": float(row["Hz_km_s_Mpc"]),
                    "sigma_H_km_s_Mpc": float(row["sigma_H_km_s_Mpc"]),
                }
            )
    return rows


def load_bao(path: Path) -> list[dict[str, float | str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, float | str]] = []
        for row in reader:
            rows.append(
                {
                    "z": float(row["z"]),
                    "value_at_z": float(row["value_at_z"]),
                    "quantity": row["quantity"],
                }
            )
    return rows


def load_pantheon(path: Path) -> list[dict[str, float | str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows: list[dict[str, float | str]] = []
        for row in reader:
            rows.append(
                {
                    "CID": row["CID"],
                    "IDSURVEY": row["IDSURVEY"],
                    "zHD": float(row["zHD"]),
                    "MU_SH0ES": float(row["MU_SH0ES"]),
                    "MU_SH0ES_ERR_DIAG": float(row["MU_SH0ES_ERR_DIAG"]),
                }
            )
    return rows


def load_csv_matrix(path: Path) -> np.ndarray:
    return np.loadtxt(path, delimiter=",", dtype=float)


def load_npy_matrix(path: Path) -> np.ndarray:
    return np.load(path)


def write_residual_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def weighted_chi_square(residuals: np.ndarray, sigma: np.ndarray) -> float:
    safe_sigma = np.where(sigma > 0, sigma, np.nan)
    return float(np.nansum((residuals / safe_sigma) ** 2))


def correlated_chi_square(residuals: np.ndarray, covariance: np.ndarray) -> float:
    if covariance.shape[0] != covariance.shape[1]:
        raise ValueError("Covariance matrix must be square")
    if covariance.shape[0] != residuals.size:
        raise ValueError("Residual vector and covariance dimensions do not match")

    jitter = np.eye(covariance.shape[0], dtype=float) * 1e-12
    solved = np.linalg.solve(covariance + jitter, residuals)
    return float(residuals.T @ solved)


def best_fit_offset(observed: np.ndarray, predicted: np.ndarray, sigma: np.ndarray) -> float:
    weights = np.where(sigma > 0, 1.0 / (sigma**2), 0.0)
    numerator = float(np.sum(weights * (observed - predicted)))
    denominator = float(np.sum(weights))
    return numerator / denominator if denominator else 0.0


def summarize_chronometers(rows: list[dict[str, float]]) -> dict[str, object]:
    z = np.array([row["z"] for row in rows], dtype=float)
    observed = np.array([row["Hz_km_s_Mpc"] for row in rows], dtype=float)
    sigma = np.array([row["sigma_H_km_s_Mpc"] for row in rows], dtype=float)
    predicted = hubble_parameter(z)
    residuals = observed - predicted
    chi2 = weighted_chi_square(residuals, sigma)
    dof = max(len(rows) - 2, 1)
    residual_rows = [
        {
            "z": float(z[index]),
            "observable": "H(z)",
            "observed": float(observed[index]),
            "predicted": float(predicted[index]),
            "residual": float(residuals[index]),
            "sigma": float(sigma[index]),
            "standardized_residual": float(residuals[index] / sigma[index]),
        }
        for index in range(len(rows))
    ]
    return {
        "rows": len(rows),
        "z_min": float(np.min(z)),
        "z_max": float(np.max(z)),
        "chi2": chi2,
        "dof": dof,
        "reduced_chi2": chi2 / dof,
        "rmse": float(np.sqrt(np.mean(residuals**2))),
        "max_abs_residual": float(np.max(np.abs(residuals))),
        "residual_rows": residual_rows,
    }


def summarize_bao(rows: list[dict[str, float | str]]) -> dict[str, object]:
    z = np.array([float(row["z"]) for row in rows], dtype=float)
    observed = np.array([float(row["value_at_z"]) for row in rows], dtype=float)
    quantities = [str(row["quantity"]) for row in rows]
    predicted = np.zeros_like(observed)

    d_m = comoving_distance(z)
    d_h = SPEED_OF_LIGHT_KM_S / hubble_parameter(z)
    d_v = (z * d_m**2 * d_h) ** (1.0 / 3.0)
    ratio_map = {
        "DM_over_rs": d_m / RS_REF_MPC,
        "DH_over_rs": d_h / RS_REF_MPC,
        "DV_over_rs": d_v / RS_REF_MPC,
    }
    for index, quantity in enumerate(quantities):
        if quantity not in ratio_map:
            raise ValueError(f"Unsupported BAO quantity: {quantity}")
        predicted[index] = float(ratio_map[quantity][index])

    residuals = observed - predicted
    sigma = np.maximum(np.abs(observed) * 0.03, 1e-6)
    chi2 = weighted_chi_square(residuals, sigma)
    covariance = load_csv_matrix(prepared_data_dir() / "desi_bao_all_gccomb_cov.csv")
    correlated = correlated_chi_square(residuals, covariance)
    dof = max(len(rows) - 3, 1)
    residual_rows = [
        {
            "z": float(z[index]),
            "observable": quantities[index],
            "observed": float(observed[index]),
            "predicted": float(predicted[index]),
            "residual": float(residuals[index]),
            "sigma": float(sigma[index]),
            "standardized_residual": float(residuals[index] / sigma[index]),
        }
        for index in range(len(rows))
    ]
    return {
        "rows": len(rows),
        "z_min": float(np.min(z)),
        "z_max": float(np.max(z)),
        "quantities": sorted(set(quantities)),
        "chi2": chi2,
        "chi2_correlated": correlated,
        "dof": dof,
        "reduced_chi2": chi2 / dof,
        "reduced_chi2_correlated": correlated / dof,
        "rmse": float(np.sqrt(np.mean(residuals**2))),
        "max_abs_residual": float(np.max(np.abs(residuals))),
        "residual_rows": residual_rows,
    }


def summarize_pantheon(rows: list[dict[str, float | str]]) -> dict[str, object]:
    z = np.array([float(row["zHD"]) for row in rows], dtype=float)
    observed = np.array([float(row["MU_SH0ES"]) for row in rows], dtype=float)
    sigma = np.array([float(row["MU_SH0ES_ERR_DIAG"]) for row in rows], dtype=float)
    predicted = distance_modulus(z)
    offset = best_fit_offset(observed, predicted, sigma)
    residuals = observed - (predicted + offset)
    chi2 = weighted_chi_square(residuals, sigma)
    covariance = load_npy_matrix(prepared_data_dir() / "pantheon_plus_shoes_statsys_cov.npy")
    ones = np.ones_like(residuals)
    covariance_inv_residuals = np.linalg.solve(covariance + np.eye(covariance.shape[0]) * 1e-12, residuals)
    covariance_inv_ones = np.linalg.solve(covariance + np.eye(covariance.shape[0]) * 1e-12, ones)
    correlated_offset = float(ones.T @ covariance_inv_residuals / (ones.T @ covariance_inv_ones))
    correlated_residuals = observed - (predicted + correlated_offset)
    correlated = correlated_chi_square(correlated_residuals, covariance)
    dof = max(len(rows) - 2, 1)
    residual_rows = [
        {
            "z": float(z[index]),
            "observable": "MU_SH0ES",
            "observed": float(observed[index]),
            "predicted": float(predicted[index] + correlated_offset),
            "residual": float(correlated_residuals[index]),
            "sigma": float(sigma[index]),
            "standardized_residual": float(correlated_residuals[index] / sigma[index]),
        }
        for index in range(len(rows))
    ]
    return {
        "rows": len(rows),
        "z_min": float(np.min(z)),
        "z_max": float(np.max(z)),
        "best_fit_offset": offset,
        "best_fit_offset_correlated": correlated_offset,
        "chi2": chi2,
        "chi2_correlated": correlated,
        "dof": dof,
        "reduced_chi2": chi2 / dof,
        "reduced_chi2_correlated": correlated / dof,
        "rmse": float(np.sqrt(np.mean(residuals**2))),
        "max_abs_residual": float(np.max(np.abs(residuals))),
        "residual_rows": residual_rows,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    outdir = v29_result_dir(output_dir) / "v29_test1_comparison"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    prepared_dir = prepared_data_dir()

    chronometers = summarize_chronometers(load_chronometers(prepared_dir / "cosmic_chronometers_hz.csv"))
    bao = summarize_bao(load_bao(prepared_dir / "desi_bao_all_gccomb_mean.csv"))
    pantheon = summarize_pantheon(load_pantheon(prepared_dir / "pantheon_plus_shoes.csv"))

    residual_dir = outdir / "residuals"
    write_residual_csv(residual_dir / "chronometers_residuals.csv", chronometers["residual_rows"])
    write_residual_csv(residual_dir / "bao_residuals.csv", bao["residual_rows"])
    write_residual_csv(residual_dir / "pantheon_residuals.csv", pantheon["residual_rows"])

    top_residuals = []
    for dataset_name, dataset in (
        ("chronometers", chronometers),
        ("bao", bao),
        ("pantheon_plus_shoes", pantheon),
    ):
        rows = dataset["residual_rows"]
        ranked = sorted(rows, key=lambda row: abs(float(row["residual"])), reverse=True)[:5]
        top_residuals.append(
            {
                "dataset": dataset_name,
                "rows": [
                    {
                        "z": float(row["z"]),
                        "observable": row["observable"],
                        "residual": float(row["residual"]),
                        "standardized_residual": float(row["standardized_residual"]),
                    }
                    for row in ranked
                ],
            }
        )

    all_reduced = [
        chronometers["reduced_chi2"],
        bao["reduced_chi2_correlated"],
        pantheon["reduced_chi2_correlated"],
    ]
    supported = all(value < 5.0 for value in all_reduced)

    payload = {
        "section": "V29-T1-DATA-COMPARISON",
        "timestamp": timestamp,
        "hypothesis": "the prepared test 1 observations follow a flat LCDM reference at the broad-shape level",
        "reference_model": {
            "type": "flat_lcdm",
            "H0_km_s_Mpc": H0_REF,
            "Omega_m": OMEGA_M_REF,
            "r_s_Mpc": RS_REF_MPC,
        },
        "method": "diagonal chi-square for H(z); correlated chi-square for DESI BAO and Pantheon+SH0ES",
        "datasets": {
            "chronometers": chronometers,
            "bao": bao,
            "pantheon_plus_shoes": pantheon,
        },
        "summary": {
            "max_reduced_chi2": max(all_reduced),
            "min_reduced_chi2": min(all_reduced),
            "mean_reduced_chi2": float(sum(all_reduced) / len(all_reduced)),
            "chronometers_reduced_chi2": chronometers["reduced_chi2"],
            "bao_reduced_chi2_correlated": bao["reduced_chi2_correlated"],
            "pantheon_reduced_chi2_correlated": pantheon["reduced_chi2_correlated"],
        },
        "residual_exports": {
            "chronometers": str(residual_dir / "chronometers_residuals.csv"),
            "bao": str(residual_dir / "bao_residuals.csv"),
            "pantheon_plus_shoes": str(residual_dir / "pantheon_residuals.csv"),
        },
        "top_abs_residuals": top_residuals,
        "verdict": "supported" if supported else "partial",
        "note": "H(z) uses diagonal errors; BAO and Pantheon+SH0ES use the prepared covariance matrices.",
    }

    json_path = outdir / f"v29test1_compare_check_{timestamp}.json"
    txt_path = outdir / f"v29test1_compare_check_{timestamp}.txt"
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    write_report(json_path, payload)

    txt_lines = [
        "V29 test 1 data comparison",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"chronometers_reduced_chi2: {chronometers['reduced_chi2']:.6f}",
        f"bao_reduced_chi2_correlated: {bao['reduced_chi2_correlated']:.6f}",
        f"pantheon_reduced_chi2_correlated: {pantheon['reduced_chi2_correlated']:.6f}",
        f"mean_reduced_chi2: {payload['summary']['mean_reduced_chi2']:.6f}",
        "",
        "Top residual slices:",
    ]
    for block in top_residuals:
        txt_lines.append(f"- {block['dataset']}")
        for row in block["rows"]:
            txt_lines.append(
                f"  z={row['z']:.5f} {row['observable']}: residual={row['residual']:.6f}, standardized={row['standardized_residual']:.6f}"
            )
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare the prepared V29 test 1 datasets against a flat LCDM reference.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()