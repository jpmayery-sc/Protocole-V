"""Run the V80 BBN delta_EM scan and summarize the accepted band."""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def z_score(model: float, obs: float, sigma_obs: float, sigma_model: float = 0.0) -> float:
    return abs(model - obs) / math.sqrt(sigma_obs**2 + sigma_model**2)


def toy_bbn_proxy(delta_em: float) -> dict[str, float]:
    """Toy proxy for the V80 scan.

    delta_em is dimensionless and expected to be negative in the scan.
    The response is intentionally explicit and monotonic so the accepted band
    can be reproduced by an external tester without hidden tuning.
    """

    deuterium_base = 2.45e-5
    he4_base = 0.24709
    li7_base = 5.24e-10
    be7_base = 4.15e-10

    deuterium = deuterium_base * math.exp(-4.65 * delta_em)
    he4 = he4_base + 0.05 * delta_em
    li7 = li7_base * math.exp(175.0 * delta_em)
    be7 = be7_base * math.exp(165.0 * delta_em)

    return {
        "D_over_H": deuterium,
        "Y_p": he4,
        "Li7_over_H": li7,
        "Be7_over_H": be7,
    }


def accepted_band(result_rows: list[dict[str, float]]) -> list[dict[str, float]]:
    d_obs = 2.527e-5
    d_sigma = 0.030e-5
    y_obs = 0.2465
    y_sigma = 0.0097
    li_obs = 1.58e-10
    li_sigma = 0.31e-10

    accepted_rows: list[dict[str, float]] = []
    for row in result_rows:
        delta_em = row["delta_em"]
        d_z = z_score(row["D_over_H"], d_obs, d_sigma)
        y_z = z_score(row["Y_p"], y_obs, y_sigma)
        li_z = z_score(row["Li7_over_H"], li_obs, li_sigma)
        row["D_z"] = d_z
        row["Y_z"] = y_z
        row["Li_z"] = li_z
        row["passes_D"] = d_z <= 1.0
        row["passes_Y"] = y_z <= 1.0
        row["passes_Li"] = li_z <= 1.0
        row["passes_all"] = row["passes_D"] and row["passes_Y"] and row["passes_Li"]
        if row["passes_all"]:
            accepted_rows.append(row)
    return accepted_rows


def scan_delta_em(delta_min: float, delta_max: float, step: float) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    current = delta_min
    while current <= delta_max + 1e-12:
        abundances = toy_bbn_proxy(current)
        rows.append({"delta_em": current, **abundances})
        current = round(current + step, 12)
    return rows


def write_csv(rows: list[dict[str, float]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["delta_em", "D_over_H", "Y_p", "Li7_over_H", "Be7_over_H", "D_z", "Y_z", "Li_z", "passes_D", "passes_Y", "passes_Li", "passes_all"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot_scan(rows: list[dict[str, float]], accepted_rows: list[dict[str, float]], output_dir: Path) -> list[str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    accepted_points = {row["delta_em"] for row in accepted_rows}
    plotted_paths: list[str] = []

    series_specs = [
        ("D_over_H", 2.527e-5, 0.030e-5, "D/H vs delta_EM", "D/H"),
        ("Y_p", 0.2465, 0.0097, "Y_p vs delta_EM", "Y_p"),
        ("Li7_over_H", 1.58e-10, 0.31e-10, "Li-7/H vs delta_EM", "Li-7/H"),
    ]

    deltas = [row["delta_em"] for row in rows]
    for key, obs, sigma, title, ylabel in series_specs:
        values = [row[key] for row in rows]
        plt.figure(figsize=(8, 5))
        plt.plot(deltas, values, color="#1f4e79", linewidth=2, label="V80 proxy")
        plt.axhspan(obs - sigma, obs + sigma, color="#d9ead3", alpha=0.8, label="bande observationnelle 1σ")
        if accepted_rows:
            accepted_deltas = [row["delta_em"] for row in rows if row["delta_em"] in accepted_points]
            accepted_values = [row[key] for row in rows if row["delta_em"] in accepted_points]
            plt.scatter(accepted_deltas, accepted_values, color="#cc0000", s=18, label="bande acceptée")
        plt.title(title)
        plt.xlabel("delta_EM")
        plt.ylabel(ylabel)
        plt.grid(True, alpha=0.25)
        plt.legend(loc="best")
        path = output_dir / f"{key}_vs_delta_em.png"
        plt.tight_layout()
        plt.savefig(path, dpi=160)
        plt.close()
        plotted_paths.append(str(path))
    return plotted_paths


def summarize(rows: list[dict[str, float]], accepted_rows: list[dict[str, float]], output_dir: Path, csv_path: Path, plot_paths: list[str]) -> dict[str, object]:
    d_obs = 2.527e-5
    d_sigma = 0.030e-5
    y_obs = 0.2465
    y_sigma = 0.0097
    li_obs = 1.58e-10
    li_sigma = 0.31e-10

    if accepted_rows:
        delta_min = min(row["delta_em"] for row in accepted_rows)
        delta_max = max(row["delta_em"] for row in accepted_rows)
        delta_center = (delta_min + delta_max) / 2.0
    else:
        delta_min = None
        delta_max = None
        delta_center = None

    best_row = min(
        rows,
        key=lambda row: z_score(row["D_over_H"], d_obs, d_sigma) + z_score(row["Y_p"], y_obs, y_sigma) + z_score(row["Li7_over_H"], li_obs, li_sigma),
    )

    accepted_count = len(accepted_rows)
    total = len(rows)
    global_verdict = "band_confirmed" if accepted_count else "no_full_band"

    summary = {
        "suite": "v80_bbn_scan",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": global_verdict,
        "v80_global_verdict": global_verdict,
        "accepted_count": accepted_count,
        "total": total,
        "delta_em_min_acceptable": delta_min,
        "delta_em_max_acceptable": delta_max,
        "delta_em_central_value": delta_center,
        "best_fit_delta_em": best_row["delta_em"],
        "best_fit": best_row,
        "accepted_rows": accepted_rows,
        "csv_path": str(csv_path),
        "plot_paths": plot_paths,
        "notes": [
            "V80 = BBN only, mécanisme paramétré par delta_EM, sans Lagrangien.",
            "pi_n_BBN, eta_b et N_eff sont tenus fixes dans le proxy.",
        ],
    }
    return summary


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v80_bbn_scan_summary_{timestamp}.json"
    txt_path = output_dir / f"v80_bbn_scan_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V80 BBN delta_EM scan summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"accepted_count: {summary['accepted_count']}/{summary['total']}",
        f"delta_em_min_acceptable: {summary['delta_em_min_acceptable']}",
        f"delta_em_max_acceptable: {summary['delta_em_max_acceptable']}",
        f"delta_em_central_value: {summary['delta_em_central_value']}",
        f"best_fit_delta_em: {summary['best_fit_delta_em']}",
        f"csv_path: {summary['csv_path']}",
        "plot_paths:",
    ]
    for path in summary["plot_paths"]:
        lines.append(f"- {path}")
    lines.append("")
    lines.append("Best fit:")
    best_fit = summary["best_fit"]
    lines.append(
        f"- delta_em={best_fit['delta_em']:.6f}, D/H={best_fit['D_over_H']:.6e}, Y_p={best_fit['Y_p']:.6f}, Li/H={best_fit['Li7_over_H']:.6e}"
    )
    lines.append("")
    lines.append("Notes:")
    for note in summary["notes"]:
        lines.append(f"- {note}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_scan(delta_min: float, delta_max: float, step: float, output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v80_bbn"
    rows = scan_delta_em(delta_min, delta_max, step)
    accepted_rows = accepted_band(rows)

    csv_path = result_dir / "v80_bbn_scan_table.csv"
    write_csv(rows, csv_path)
    plot_paths = plot_scan(rows, accepted_rows, result_dir / "plots")

    summary = summarize(rows, accepted_rows, result_dir, csv_path, plot_paths)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V80 BBN delta_EM scan and summarize the accepted band.")
    parser.add_argument("--delta-min", type=float, default=-0.020, help="Minimum delta_EM value to scan")
    parser.add_argument("--delta-max", type=float, default=-0.001, help="Maximum delta_EM value to scan")
    parser.add_argument("--step", type=float, default=0.0001, help="Scan step for delta_EM")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_scan(args.delta_min, args.delta_max, args.step, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()