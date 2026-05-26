"""Run the V77 physical-resolution diagnostic for lithium around the V80B fixed point."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

from runv80_bbn_scan import toy_bbn_proxy, workspace_root, z_score


V80B_REFERENCE = {
    "delta_em": -0.0069,
    "D_over_H": 2.52988e-5,
    "Y_p": 0.246745,
    "Li7_over_H": 1.56647e-10,
    "Be7_over_H": 1.32924e-10,
}


def evaluate_point(delta_em: float, li_scale: float = 1.0, be_scale: float = 1.0) -> dict[str, float | bool]:
    abundances = toy_bbn_proxy(delta_em)

    d_obs = 2.527e-5
    d_sigma = 0.030e-5
    y_obs = 0.2465
    y_sigma = 0.0097
    li_obs = 1.58e-10
    li_sigma = 0.31e-10

    li_direct = abundances["Li7_over_H"] * li_scale
    be_feeddown = abundances["Be7_over_H"] * be_scale
    li_total = li_direct + be_feeddown

    d_z = z_score(abundances["D_over_H"], d_obs, d_sigma)
    y_z = z_score(abundances["Y_p"], y_obs, y_sigma)
    li_direct_z = z_score(li_direct, li_obs, li_sigma)
    li_total_z = z_score(li_total, li_obs, li_sigma)

    return {
        "delta_em": delta_em,
        "li_scale": li_scale,
        "be_scale": be_scale,
        "D_over_H": abundances["D_over_H"],
        "Y_p": abundances["Y_p"],
        "Li7_over_H": li_direct,
        "Be7_over_H": be_feeddown,
        "Li_total_over_H": li_total,
        "D_z": d_z,
        "Y_z": y_z,
        "Li7_z": li_direct_z,
        "Li_total_z": li_total_z,
        "passes_D": d_z <= 1.0,
        "passes_Y": y_z <= 1.0,
        "passes_Li7": li_direct_z <= 1.0,
        "passes_Li_total": li_total_z <= 1.0,
        "passes_all_direct": d_z <= 1.0 and y_z <= 1.0 and li_direct_z <= 1.0,
        "passes_all_total": d_z <= 1.0 and y_z <= 1.0 and li_total_z <= 1.0,
    }


def scan_window(delta_min: float, delta_max: float, step: float) -> list[dict[str, float | bool]]:
    rows: list[dict[str, float | bool]] = []
    current = delta_min
    while current <= delta_max + 1e-12:
        rows.append(evaluate_point(current))
        current = round(current + step, 12)
    return rows


def write_csv(rows: list[dict[str, float | bool]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "delta_em",
        "li_scale",
        "be_scale",
        "D_over_H",
        "Y_p",
        "Li7_over_H",
        "Be7_over_H",
        "Li_total_over_H",
        "D_z",
        "Y_z",
        "Li7_z",
        "Li_total_z",
        "passes_D",
        "passes_Y",
        "passes_Li7",
        "passes_Li_total",
        "passes_all_direct",
        "passes_all_total",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot_scan(rows: list[dict[str, float | bool]], output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    plotted: list[str] = []

    series = [
        ("D_over_H", 2.527e-5, 0.030e-5, "D/H vs delta_EM", "D/H"),
        ("Y_p", 0.2465, 0.0097, "Y_p vs delta_EM", "Y_p"),
        ("Li7_over_H", 1.58e-10, 0.31e-10, "Li-7/H vs delta_EM", "Li-7/H"),
        ("Li_total_over_H", 1.58e-10, 0.31e-10, "Li-7 + Be-7 vs delta_EM", "Li total proxy"),
    ]

    deltas = [float(row["delta_em"]) for row in rows]
    for key, obs, sigma, title, ylabel in series:
        values = [float(row[key]) for row in rows]
        plt.figure(figsize=(8, 5))
        plt.plot(deltas, values, color="#1f4e79", linewidth=2, label="V77 proxy")
        plt.axhspan(obs - sigma, obs + sigma, color="#d9ead3", alpha=0.8, label="bande observationnelle 1σ")
        plt.axvline(-0.0069, color="#cc0000", linestyle="--", linewidth=1.5, label="epsilon_best")
        plt.title(title)
        plt.xlabel("delta_EM")
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.25)
        plt.legend(loc="best")
        path = output_dir / f"{key}_vs_delta_em.png"
        plt.tight_layout()
        plt.savefig(path, dpi=160)
        plt.close()
        plotted.append(str(path))
    return plotted


def band_summary(rows: list[dict[str, float | bool]], key: str) -> dict[str, float | int | None]:
    accepted = [row for row in rows if bool(row[key]) and bool(row["passes_D"]) and bool(row["passes_Y"])]
    if not accepted:
        return {"count": 0, "delta_min": None, "delta_max": None, "delta_width": None}

    delta_min = min(float(row["delta_em"]) for row in accepted)
    delta_max = max(float(row["delta_em"]) for row in accepted)
    return {
        "count": len(accepted),
        "delta_min": delta_min,
        "delta_max": delta_max,
        "delta_width": delta_max - delta_min,
    }


def finite_difference(rows: list[dict[str, float | bool]], key: str, center_index: int) -> float | None:
    if center_index <= 0 or center_index >= len(rows) - 1:
        return None
    left = rows[center_index - 1]
    right = rows[center_index + 1]
    dx = float(right["delta_em"]) - float(left["delta_em"])
    if dx == 0:
        return None
    return (float(right[key]) - float(left[key])) / dx


def evaluate_rate_robustness(delta_em: float) -> list[dict[str, float | bool]]:
    rows: list[dict[str, float | bool]] = []
    for li_scale, be_scale in itertools.product([0.95, 1.0, 1.05], repeat=2):
        rows.append(evaluate_point(delta_em, li_scale=li_scale, be_scale=be_scale))
    return rows


def control_match(center: dict[str, float | bool]) -> dict[str, float]:
    return {
        "delta_em_abs_error": abs(float(center["delta_em"]) - V80B_REFERENCE["delta_em"]),
        "D_over_H_abs_error": abs(float(center["D_over_H"]) - V80B_REFERENCE["D_over_H"]),
        "Y_p_abs_error": abs(float(center["Y_p"]) - V80B_REFERENCE["Y_p"]),
        "Li7_over_H_abs_error": abs(float(center["Li7_over_H"]) - V80B_REFERENCE["Li7_over_H"]),
        "Be7_over_H_abs_error": abs(float(center["Be7_over_H"]) - V80B_REFERENCE["Be7_over_H"]),
    }


def summarize(rows: list[dict[str, float | bool]], plot_paths: list[str], csv_path: Path, output_dir: Path) -> dict[str, object]:
    center_index = min(range(len(rows)), key=lambda i: abs(float(rows[i]["delta_em"]) + 0.0069))
    center = rows[center_index]

    d_band = band_summary(rows, "passes_D")
    y_band = band_summary(rows, "passes_Y")
    li7_band = band_summary(rows, "passes_Li7")
    li_total_band = band_summary(rows, "passes_Li_total")

    rate_rows = evaluate_rate_robustness(-0.0069)
    rate_passes_direct = sum(1 for row in rate_rows if bool(row["passes_all_direct"]))
    rate_passes_total = sum(1 for row in rate_rows if bool(row["passes_all_total"]))
    rate_total = len(rate_rows)

    d_slope = finite_difference(rows, "D_over_H", center_index)
    y_slope = finite_difference(rows, "Y_p", center_index)
    li7_slope = finite_difference(rows, "Li7_over_H", center_index)
    li_total_slope = finite_difference(rows, "Li_total_over_H", center_index)

    control_errors = control_match(center)
    control_tolerances = {
        "delta_em_abs_error": 1e-12,
        "D_over_H_abs_error": 1e-10,
        "Y_p_abs_error": 1e-6,
        "Li7_over_H_abs_error": 1e-12,
        "Be7_over_H_abs_error": 1e-12,
    }
    control_ok = all(control_errors[name] <= tolerance for name, tolerance in control_tolerances.items())

    li_selectivity = None
    if d_slope is not None and y_slope is not None and li7_slope is not None:
        denominator = max(abs(d_slope), abs(y_slope), 1e-30)
        li_selectivity = abs(li7_slope) / denominator

    if control_ok and bool(center["passes_all_direct"]) and bool(center["passes_all_total"]) and rate_passes_total == rate_total:
        verdict = "resolution_robuste"
        verdict_text = "Li résolu de façon robuste"
    elif control_ok and bool(center["passes_all_direct"]):
        verdict = "resolution_fine"
        verdict_text = "Li résolu de façon fine"
    else:
        verdict = "tension_persistante"
        verdict_text = "Li non résolu"

    summary = {
        "suite": "v77_li_physical_resolution",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "verdict_text": verdict_text,
        "delta_center": -0.0069,
        "scan_min": float(rows[0]["delta_em"]),
        "scan_max": float(rows[-1]["delta_em"]),
        "scan_step": float(rows[1]["delta_em"]) - float(rows[0]["delta_em"]) if len(rows) > 1 else None,
        "scan_count": len(rows),
        "control_ok": control_ok,
        "control_tolerances": control_tolerances,
        "control_errors": control_errors,
        "center_point": center,
        "bands": {
            "D_over_H": d_band,
            "Y_p": y_band,
            "Li7_over_H": li7_band,
            "Li_total_over_H": li_total_band,
        },
        "slopes_at_center": {
            "D_over_H": d_slope,
            "Y_p": y_slope,
            "Li7_over_H": li7_slope,
            "Li_total_over_H": li_total_slope,
            "Li_selectivity": li_selectivity,
        },
        "rate_robustness": {
            "grid": [0.95, 1.0, 1.05],
            "total_cases": rate_total,
            "passes_all_direct": rate_passes_direct,
            "passes_all_total": rate_passes_total,
        },
        "csv_path": str(csv_path),
        "plot_paths": plot_paths,
        "output_dir": str(output_dir),
    }
    return summary


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v77_li_physical_resolution_summary_{timestamp}.json"
    txt_path = output_dir / f"v77_li_physical_resolution_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    center = summary["center_point"]
    lines = [
        "V77 lithium physical-resolution summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"verdict_text: {summary['verdict_text']}",
        f"delta_center: {summary['delta_center']}",
        f"scan_window: [{summary['scan_min']}, {summary['scan_max']}], step={summary['scan_step']}",
        f"scan_count: {summary['scan_count']}",
        f"control_ok: {summary['control_ok']}",
        f"center_D_over_H: {center['D_over_H']}",
        f"center_Y_p: {center['Y_p']}",
        f"center_Li7_over_H: {center['Li7_over_H']}",
        f"center_Be7_over_H: {center['Be7_over_H']}",
        f"center_Li_total_over_H: {center['Li_total_over_H']}",
        f"center_passes_all_direct: {center['passes_all_direct']}",
        f"center_passes_all_total: {center['passes_all_total']}",
        "",
        "Control errors:",
    ]
    for name, value in summary["control_errors"].items():
        lines.append(f"- {name}: {value}")
    lines.extend([
        "",
        "Control tolerances:",
    ])
    for name, value in summary["control_tolerances"].items():
        lines.append(f"- {name}: {value}")
    lines.extend([
        "",
        "Bands:",
    ])
    for name, band in summary["bands"].items():
        lines.append(f"- {name}: {band}")
    lines.extend([
        "",
        "Slopes at center:",
    ])
    for name, slope in summary["slopes_at_center"].items():
        lines.append(f"- {name}: {slope}")
    lines.extend([
        "",
        "Rate robustness:",
        f"- total_cases: {summary['rate_robustness']['total_cases']}",
        f"- passes_all_direct: {summary['rate_robustness']['passes_all_direct']}",
        f"- passes_all_total: {summary['rate_robustness']['passes_all_total']}",
        "",
        "Plots:",
    ])
    for path in summary["plot_paths"]:
        lines.append(f"- {path}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_resolution(
    delta_min: float,
    delta_max: float,
    step: float,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77_li_physical_resolution"

    rows = scan_window(delta_min, delta_max, step)
    csv_path = result_dir / "v77_li_physical_resolution_scan.csv"
    write_csv(rows, csv_path)
    plot_paths = plot_scan(rows, result_dir / "plots")

    summary = summarize(rows, plot_paths, csv_path, result_dir)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77 physical-resolution diagnostic for lithium.")
    parser.add_argument("--delta-min", type=float, default=-0.0072, help="Minimum delta_EM value to scan")
    parser.add_argument("--delta-max", type=float, default=-0.0066, help="Maximum delta_EM value to scan")
    parser.add_argument("--step", type=float, default=0.00001, help="Scan step for delta_EM")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_resolution(args.delta_min, args.delta_max, args.step, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()