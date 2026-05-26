"""Run the V77B EM differential stress test for Li-7, Be-7 and Li_total."""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

from runv80_bbn_scan import workspace_root, z_score


def proxy_bbn_differential(delta_em: float, alpha_be: float) -> dict[str, float]:
    deuterium_base = 2.45e-5
    he4_base = 0.24709
    li7_base = 5.24e-10
    be7_base = 4.15e-10

    delta_em_li = delta_em
    delta_em_be = alpha_be * delta_em

    return {
        "D_over_H": deuterium_base * math.exp(-4.65 * delta_em),
        "Y_p": he4_base + 0.05 * delta_em,
        "Li7_over_H": li7_base * math.exp(175.0 * delta_em_li),
        "Be7_over_H": be7_base * math.exp(165.0 * delta_em_be),
    }


def evaluate_point(delta_em: float, alpha_be: float, li_scale: float = 1.0, be_scale: float = 1.0) -> dict[str, float | bool]:
    abundances = proxy_bbn_differential(delta_em, alpha_be)

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
    li_z = z_score(li_direct, li_obs, li_sigma)
    li_total_z = z_score(li_total, li_obs, li_sigma)
    proxy_chi2 = d_z**2 + y_z**2 + li_total_z**2

    return {
        "delta_em": delta_em,
        "alpha_be": alpha_be,
        "li_scale": li_scale,
        "be_scale": be_scale,
        "D_over_H": abundances["D_over_H"],
        "Y_p": abundances["Y_p"],
        "Li7_over_H": li_direct,
        "Be7_over_H": be_feeddown,
        "Li_total_over_H": li_total,
        "D_z": d_z,
        "Y_z": y_z,
        "Li7_z": li_z,
        "Li_total_z": li_total_z,
        "proxy_chi2": proxy_chi2,
        "passes_D": d_z <= 1.0,
        "passes_Y": y_z <= 1.0,
        "passes_Li7": li_z <= 1.0,
        "passes_Li_total": li_total_z <= 1.0,
        "passes_all_direct": d_z <= 1.0 and y_z <= 1.0 and li_z <= 1.0,
        "passes_all_total": d_z <= 1.0 and y_z <= 1.0 and li_total_z <= 1.0,
    }


def grid_values(start: float, stop: float, count: int) -> list[float]:
    if count < 2:
        return [start]
    step = (stop - start) / (count - 1)
    return [round(start + i * step, 12) for i in range(count)]


def write_csv(rows: list[dict[str, float | bool]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "delta_em",
        "alpha_be",
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
        "proxy_chi2",
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


def plot_heatmap(rows: list[dict[str, float | bool]], key: str, output_dir: Path, title: str, ylabel: str) -> str:
    delta_values = sorted({float(row["delta_em"]) for row in rows})
    alpha_values = sorted({float(row["alpha_be"]) for row in rows})
    matrix = [[0.0 for _ in alpha_values] for _ in delta_values]
    for row in rows:
        i = delta_values.index(float(row["delta_em"]))
        j = alpha_values.index(float(row["alpha_be"]))
        matrix[i][j] = float(row[key])

    plt.figure(figsize=(8, 5))
    plt.imshow(matrix, origin="lower", aspect="auto", cmap="viridis", extent=[min(alpha_values), max(alpha_values), min(delta_values), max(delta_values)])
    plt.colorbar(label=ylabel)
    plt.title(title)
    plt.xlabel("alpha_Be")
    plt.ylabel("delta_EM")
    plt.axhline(-0.0069, color="#cc0000", linestyle="--", linewidth=1.2)
    path = output_dir / f"{key}_heatmap.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return str(path)


def summarize(rows: list[dict[str, float | bool]], csv_path: Path, plot_paths: list[str], output_dir: Path) -> dict[str, object]:
    direct_rows = [row for row in rows if bool(row["passes_all_direct"]) ]
    total_rows = [row for row in rows if bool(row["passes_all_total"]) ]

    if total_rows:
        best_row = min(total_rows, key=lambda row: float(row["proxy_chi2"]))
    else:
        best_row = min(rows, key=lambda row: float(row["proxy_chi2"]))

    alpha_best = best_row["alpha_be"]
    delta_best = best_row["delta_em"]

    if total_rows and len(total_rows) >= len(rows) * 0.15:
        verdict = "canal_em_differentiel_efficace"
        verdict_text = "direction EM différentiel utile"
    elif direct_rows:
        verdict = "resolution_ultra_fine"
        verdict_text = "direction EM différentiel tuning"
    else:
        verdict = "canal_em_differentiel_inefficace"
        verdict_text = "direction EM différentiel inutile"

    summary = {
        "suite": "v77b_em_stress_test",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "verdict_text": verdict_text,
        "scan_delta_values": sorted({float(row["delta_em"]) for row in rows}),
        "scan_alpha_values": sorted({float(row["alpha_be"]) for row in rows}),
        "row_count": len(rows),
        "direct_pass_count": len(direct_rows),
        "total_pass_count": len(total_rows),
        "best_row": best_row,
        "best_alpha_be": alpha_best,
        "best_delta_em": delta_best,
        "csv_path": str(csv_path),
        "plot_paths": plot_paths,
        "output_dir": str(output_dir),
    }
    return summary


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v77b_em_stress_test_summary_{timestamp}.json"
    txt_path = output_dir / f"v77b_em_stress_test_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    best = summary["best_row"]
    lines = [
        "V77B EM differential stress test summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"verdict_text: {summary['verdict_text']}",
        f"row_count: {summary['row_count']}",
        f"direct_pass_count: {summary['direct_pass_count']}",
        f"total_pass_count: {summary['total_pass_count']}",
        f"best_delta_em: {summary['best_delta_em']}",
        f"best_alpha_be: {summary['best_alpha_be']}",
        f"best_proxy_chi2: {best['proxy_chi2']}",
        f"best_D_over_H: {best['D_over_H']}",
        f"best_Y_p: {best['Y_p']}",
        f"best_Li7_over_H: {best['Li7_over_H']}",
        f"best_Be7_over_H: {best['Be7_over_H']}",
        f"best_Li_total_over_H: {best['Li_total_over_H']}",
        "",
        "Plots:",
    ]
    for path in summary["plot_paths"]:
        lines.append(f"- {path}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_stress_test(
    delta_min: float,
    delta_max: float,
    delta_count: int,
    alpha_min: float,
    alpha_max: float,
    alpha_count: int,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77b_em_stress_test"
    plot_dir = result_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    delta_values = grid_values(delta_min, delta_max, delta_count)
    alpha_values = grid_values(alpha_min, alpha_max, alpha_count)
    rate_grid = [0.95, 1.0, 1.05]

    rows: list[dict[str, float | bool]] = []
    for delta_em, alpha_be, li_scale, be_scale in itertools.product(delta_values, alpha_values, rate_grid, rate_grid):
        rows.append(evaluate_point(delta_em, alpha_be, li_scale=li_scale, be_scale=be_scale))

    csv_path = result_dir / "v77b_em_stress_test_grid.csv"
    write_csv(rows, csv_path)

    plot_paths = [
        plot_heatmap(rows, "Li7_over_H", plot_dir, "Li-7/H vs delta_EM and alpha_Be", "Li-7/H"),
        plot_heatmap(rows, "Be7_over_H", plot_dir, "Be-7/H vs delta_EM and alpha_Be", "Be-7/H"),
        plot_heatmap(rows, "Li_total_over_H", plot_dir, "Li_total vs delta_EM and alpha_Be", "Li_total/H"),
    ]

    summary = summarize(rows, csv_path, plot_paths, result_dir)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77B EM differential stress test.")
    parser.add_argument("--delta-min", type=float, default=-0.0072, help="Minimum delta_EM value to scan")
    parser.add_argument("--delta-max", type=float, default=-0.0066, help="Maximum delta_EM value to scan")
    parser.add_argument("--delta-count", type=int, default=5, help="Number of delta_EM sample points")
    parser.add_argument("--alpha-min", type=float, default=0.5, help="Minimum alpha_Be value to scan")
    parser.add_argument("--alpha-max", type=float, default=1.0, help="Maximum alpha_Be value to scan")
    parser.add_argument("--alpha-count", type=int, default=5, help="Number of alpha_Be sample points")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_stress_test(
        args.delta_min,
        args.delta_max,
        args.delta_count,
        args.alpha_min,
        args.alpha_max,
        args.alpha_count,
        args.output_dir,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()