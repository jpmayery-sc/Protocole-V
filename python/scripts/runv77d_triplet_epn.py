"""Run the V77D triplet e-p-n diagnostic for electronic compensation of A=7."""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

from runv80_bbn_scan import workspace_root, z_score


def proxy_bbn_electron(delta_em: float, beta_e: float) -> dict[str, float]:
    delta_eff = delta_em * beta_e

    deuterium_base = 2.45e-5
    he4_base = 0.24709
    li7_base = 5.24e-10
    be7_base = 4.15e-10

    li7 = li7_base * math.exp(175.0 * delta_eff)
    be7 = be7_base * math.exp(165.0 * delta_eff)
    be7_eff = be7 * (1 - 0.3 * (beta_e - 1.0))

    return {
        "D_over_H": deuterium_base * math.exp(-4.65 * delta_eff),
        "Y_p": he4_base + 0.05 * delta_eff,
        "Li7_over_H": li7,
        "Be7_over_H": be7_eff,
        "Li_total_over_H": li7 + be7_eff,
        "delta_em_eff": delta_eff,
    }


def evaluate_point(beta_e: float) -> dict[str, float | bool]:
    abundances = proxy_bbn_electron(-0.0069, beta_e)

    d_obs = 2.527e-5
    d_sigma = 0.030e-5
    y_obs = 0.2465
    y_sigma = 0.0097
    li_obs = 1.58e-10
    li_sigma = 0.31e-10

    d_z = z_score(abundances["D_over_H"], d_obs, d_sigma)
    y_z = z_score(abundances["Y_p"], y_obs, y_sigma)
    li7_z = z_score(abundances["Li7_over_H"], li_obs, li_sigma)
    li_total_z = z_score(abundances["Li_total_over_H"], li_obs, li_sigma)

    return {
        "beta_e": beta_e,
        **abundances,
        "D_z": d_z,
        "Y_z": y_z,
        "Li7_z": li7_z,
        "Li_total_z": li_total_z,
        "passes_D": d_z <= 1.0,
        "passes_Y": y_z <= 1.0,
        "passes_Li7": li7_z <= 1.0,
        "passes_Li_total": li_total_z <= 1.0,
        "passes_all_direct": d_z <= 1.0 and y_z <= 1.0 and li7_z <= 1.0,
        "passes_all_total": d_z <= 1.0 and y_z <= 1.0 and li_total_z <= 1.0,
    }


def scan_beta(beta_min: float, beta_max: float, points: int) -> list[dict[str, float | bool]]:
    if points < 2:
        grid = [beta_min]
    else:
        step = (beta_max - beta_min) / (points - 1)
        grid = [round(beta_min + i * step, 12) for i in range(points)]
    return [evaluate_point(beta) for beta in grid]


def write_csv(rows: list[dict[str, float | bool]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "beta_e",
        "delta_em_eff",
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
    betas = [float(row["beta_e"]) for row in rows]
    series = [
        ("Li7_over_H", 1.58e-10, 0.31e-10, "Li7 vs beta_e", "Li7/H"),
        ("Be7_over_H", 1.58e-10, 0.31e-10, "Be7 vs beta_e", "Be7/H"),
        ("Li_total_over_H", 1.58e-10, 0.31e-10, "Li_total vs beta_e", "Li_total/H"),
    ]
    plotted: list[str] = []
    for key, obs, sigma, title, ylabel in series:
        values = [float(row[key]) for row in rows]
        plt.figure(figsize=(8, 5))
        plt.plot(betas, values, marker="o", linewidth=2, color="#1f4e79")
        plt.axhspan(obs - sigma, obs + sigma, color="#d9ead3", alpha=0.8, label="bande observationnelle 1σ")
        plt.axvline(1.0, color="#cc0000", linestyle="--", linewidth=1.2, label="beta_e = 1")
        plt.title(title)
        plt.xlabel("beta_e")
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.25)
        plt.legend(loc="best")
        path = output_dir / f"{key}_vs_beta_e.png"
        plt.tight_layout()
        plt.savefig(path, dpi=160)
        plt.close()
        plotted.append(str(path))
    return plotted


def summarize(rows: list[dict[str, float | bool]], csv_path: Path, plot_paths: list[str], output_dir: Path) -> dict[str, object]:
    best_row = min(rows, key=lambda row: float(row["Li_total_over_H"]))
    baseline_row = min(rows, key=lambda row: abs(float(row["beta_e"]) - 1.0))

    li_total_ratio = float(best_row["Li_total_over_H"]) / float(baseline_row["Li_total_over_H"])
    li_total_drop = 1.0 - li_total_ratio

    if li_total_drop > 0.10 and bool(best_row["passes_D"]) and bool(best_row["passes_Y"]):
        verdict = "direction_physique_ouverte"
        verdict_text = "beta_e ouvre une direction physique pour compenser A=7"
    else:
        verdict = "pas_de_direction"
        verdict_text = "beta_e n'ouvre pas de direction physique"

    summary = {
        "suite": "v77d_triplet_epn",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "verdict_text": verdict_text,
        "row_count": len(rows),
        "baseline_row": baseline_row,
        "best_row": best_row,
        "li_total_drop_fraction": li_total_drop,
        "csv_path": str(csv_path),
        "plot_paths": plot_paths,
        "output_dir": str(output_dir),
    }
    return summary


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v77d_triplet_epn_summary_{timestamp}.json"
    txt_path = output_dir / f"v77d_triplet_epn_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    best = summary["best_row"]
    baseline = summary["baseline_row"]
    lines = [
        "V77D triplet e-p-n scan summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"verdict_text: {summary['verdict_text']}",
        f"row_count: {summary['row_count']}",
        f"li_total_drop_fraction: {summary['li_total_drop_fraction']}",
        f"baseline_beta_e: {baseline['beta_e']}",
        f"baseline_Li_total_over_H: {baseline['Li_total_over_H']}",
        f"best_beta_e: {best['beta_e']}",
        f"best_Li_total_over_H: {best['Li_total_over_H']}",
        f"best_D_over_H: {best['D_over_H']}",
        f"best_Y_p: {best['Y_p']}",
        f"best_Li7_over_H: {best['Li7_over_H']}",
        f"best_Be7_over_H: {best['Be7_over_H']}",
        "",
        "Plots:",
    ]
    for path in summary["plot_paths"]:
        lines.append(f"- {path}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_scan(beta_min: float, beta_max: float, points: int, output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77d_triplet_epn"
    plot_dir = result_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    rows = scan_beta(beta_min, beta_max, points)
    csv_path = result_dir / "v77d_triplet_epn_scan.csv"
    write_csv(rows, csv_path)
    plot_paths = plot_scan(rows, plot_dir)

    summary = summarize(rows, csv_path, plot_paths, result_dir)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77D triplet e-p-n diagnostic.")
    parser.add_argument("--beta-min", type=float, default=0.8, help="Minimum beta_e value")
    parser.add_argument("--beta-max", type=float, default=1.2, help="Maximum beta_e value")
    parser.add_argument("--points", type=int, default=5, help="Number of beta_e sample points")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_scan(args.beta_min, args.beta_max, args.points, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()