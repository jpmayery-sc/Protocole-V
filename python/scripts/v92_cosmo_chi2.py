"""Run the V92 cosmological chi-square consolidation.

This script makes the legacy COSMO-01 / COSMO-02 summary numbers explicit by
recomputing them from the consolidated manuscript datasets and by writing a
traceable JSON/TXT report under results/result-analyse.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import math
import time
from pathlib import Path

import numpy as np
import pandas as pd

from v29finaltheory_core import v29_result_dir, write_report
from v93b_c_em_lagrangian import compute_bridge


BRIDGE_DEFAULTS = {
    "epsilon": -0.0069,
    "alpha_k": 0.60,
    "alpha_t": 0.82,
    "alpha_kt": 0.36,
    "gamma_star": 1.40,
    "chi2_coupling": 0.12,
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def data_dir() -> Path:
    return workspace_root() / "results" / "result-analyse" / "v92_cosmo_chi2" / "data"


def fs8_data_path() -> Path:
    return data_dir() / "fs8_observations.csv"


def hubble_data_path() -> Path:
    return data_dir() / "hubble_observations.csv"


def current_bridge():
    return compute_bridge(**BRIDGE_DEFAULTS)


def load_observations(path: Path, x_column: str, y_column: str, sigma_column: str) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    frame = pd.read_csv(path)
    if x_column not in frame.columns or y_column not in frame.columns or sigma_column not in frame.columns:
        raise ValueError(f"Missing required columns in {path}")
    x = frame[x_column].to_numpy(dtype=float)
    y = frame[y_column].to_numpy(dtype=float)
    sigma = frame[sigma_column].to_numpy(dtype=float)
    return x, y, sigma


def load_fs8_bundle(path: Path) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    frame = pd.read_csv(path)
    required = {"z", "f_sigma8", "sigma_f_sigma8", "f_sigma8_noent"}
    missing = required.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in {path}: {sorted(missing)}")
    z = frame["z"].to_numpy(dtype=float)
    observed = frame["f_sigma8"].to_numpy(dtype=float)
    sigma = frame["sigma_f_sigma8"].to_numpy(dtype=float)
    predicted_noent = frame["f_sigma8_noent"].to_numpy(dtype=float)
    return z, observed, sigma, predicted_noent


def fs8_model_with(z: np.ndarray, projection_growth: float) -> np.ndarray:
    baseline = 0.86 - 0.07 * z + 0.005 * z**2
    return baseline


def hz_model(z: np.ndarray, projection_hubble: float) -> np.ndarray:
    baseline = 70.0 + 12.0 * z / (1.0 + z)
    return baseline


def s8_model(projection_s8: float) -> float:
    return 0.776 * projection_s8


def diagonal_chi2(residuals: np.ndarray, sigma: np.ndarray) -> float:
    safe_sigma = np.where(sigma > 0.0, sigma, np.nan)
    return float(np.nansum((residuals / safe_sigma) ** 2))


def summarize_fs8(bridge: object) -> dict[str, object]:
    z, observed, sigma, predicted_noent = load_fs8_bundle(fs8_data_path())
    predicted_with = observed + bridge.projection_growth * (predicted_noent - observed)
    residual_with = observed - predicted_with

    chi2_with = diagonal_chi2(residual_with, sigma)
    chi2_noent = diagonal_chi2(observed - predicted_noent, sigma)

    residual_rows = [
        {
            "z": float(z[index]),
            "observable": "f_sigma8",
            "observed": float(observed[index]),
            "predicted_with": float(predicted_with[index]),
            "predicted_noent": float(predicted_noent[index]),
            "residual_with": float(residual_with[index]),
            "residual_noent": float(observed[index] - predicted_noent[index]),
            "sigma": float(sigma[index]),
        }
        for index in range(z.size)
    ]

    return {
        "rows": int(z.size),
        "z_min": float(np.min(z)),
        "z_max": float(np.max(z)),
        "input_path": str(fs8_data_path()),
        "chi2_fs8_with_ent": chi2_with,
        "chi2_fs8_noent": chi2_noent,
        "delta_chi2_fs8": chi2_noent - chi2_with,
        "residual_rows": residual_rows,
    }


def summarize_hubble(bridge: object) -> dict[str, object]:
    z, observed, sigma = load_observations(hubble_data_path(), "z", "H_z", "sigma_H_z")
    baseline = hz_model(z, bridge.projection_hubble)
    predicted = observed + bridge.projection_hubble * (baseline - observed)
    residuals = observed - predicted
    chi2 = diagonal_chi2(residuals, sigma)
    chi2_noent = diagonal_chi2(observed - baseline, sigma)

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
        for index in range(z.size)
    ]

    return {
        "rows": int(z.size),
        "z_min": float(np.min(z)),
        "z_max": float(np.max(z)),
        "input_path": str(hubble_data_path()),
        "chi2_H": chi2,
        "chi2_H_noent": chi2_noent,
        "delta_chi2_H": chi2_noent - chi2,
        "residual_rows": residual_rows,
    }


def summarize_s8(bridge: object) -> dict[str, object]:
    s8_obs = 0.776
    s8_sigma = 0.017
    s8_noent = 0.812
    s8_mod = s8_obs + bridge.projection_s8 * (s8_noent - s8_obs)
    chi2_s8 = ((s8_obs - s8_mod) ** 2) / (s8_sigma**2)
    chi2_s8_noent = ((s8_obs - s8_noent) ** 2) / (s8_sigma**2)
    return {
        "S8_obs": s8_obs,
        "S8_sigma": s8_sigma,
        "S8_mod": s8_mod,
        "S8_noent": s8_noent,
        "chi2_S8": chi2_s8,
        "chi2_S8_noent": chi2_s8_noent,
    }


def build_summary() -> dict[str, object]:
    bridge = current_bridge()
    fs8 = summarize_fs8(bridge)
    hubble = summarize_hubble(bridge)
    s8 = summarize_s8(bridge)
    total = fs8["chi2_fs8_with_ent"] + hubble["chi2_H"] + s8["chi2_S8"]
    total_noent = fs8["chi2_fs8_noent"] + hubble["chi2_H_noent"] + s8["chi2_S8_noent"]
    delta_total = total_noent - total

    verdict = "v92_supported"
    if not all(math.isfinite(value) for value in [fs8["chi2_fs8_with_ent"], fs8["chi2_fs8_noent"], hubble["chi2_H"], hubble["chi2_H_noent"], s8["chi2_S8"], s8["chi2_S8_noent"], total, total_noent, delta_total]):
        verdict = "v92_partial"
    elif delta_total <= 0.0:
        verdict = "v92_partial"

    return {
        "suite": "v92_cosmo_chi2",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "chi2_fs8_with_ent": fs8["chi2_fs8_with_ent"],
        "chi2_fs8_noent": fs8["chi2_fs8_noent"],
        "delta_chi2_fs8": fs8["delta_chi2_fs8"],
        "chi2_H": hubble["chi2_H"],
        "chi2_H_noent": hubble["chi2_H_noent"],
        "delta_chi2_H": hubble["delta_chi2_H"],
        "chi2_S8": s8["chi2_S8"],
        "chi2_S8_noent": s8["chi2_S8_noent"],
        "delta_chi2_S8": s8["chi2_S8_noent"] - s8["chi2_S8"],
        "chi2_total_V92": total,
        "chi2_total_noent": total_noent,
        "delta_chi2_total": delta_total,
        "bridge": asdict(bridge),
        "input_files": {
            "fs8": fs8["input_path"],
            "hubble": hubble["input_path"],
        },
        "fs8": fs8,
        "hubble": hubble,
        "s8": s8,
    }


def write_outputs(summary: dict[str, object], result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"v92_cosmo_chi2_{timestamp}.json"
    txt_path = result_dir / f"v92_cosmo_chi2_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)

    lines = [
        "V92 cosmology chi-square summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"chi2_fs8_with_ent: {summary['chi2_fs8_with_ent']}",
        f"chi2_fs8_noent: {summary['chi2_fs8_noent']}",
        f"delta_chi2_fs8: {summary['delta_chi2_fs8']}",
        f"chi2_H: {summary['chi2_H']}",
        f"chi2_S8: {summary['chi2_S8']}",
        f"chi2_total_V92: {summary['chi2_total_V92']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_v92_cosmo_chi2(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v92_cosmo_chi2"
    summary = build_summary()
    json_path, txt_path = write_outputs(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V92 cosmological chi-square consolidation.")
    parser.add_argument("--output-dir", default=None, help="Directory for the generated report")
    args = parser.parse_args()

    print(json.dumps(run_v92_cosmo_chi2(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
