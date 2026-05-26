"""Run the V77E internal exchange and drain scan for the A=7 channel."""
from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import matplotlib.pyplot as plt

from runv80_bbn_scan import workspace_root, z_score


LI7_BASE = 1.230e-10
BE7_BASE = 9.950e-11
LI_MIN = 1.27e-10
LI_MAX = 1.89e-10


def evaluate_point(gamma_exch: float, gamma_drain: float, eta_exch: float = 1.0) -> dict[str, float | bool]:
    be7_exch = BE7_BASE * (1.0 - gamma_exch)
    li7_exch = LI7_BASE + eta_exch * (BE7_BASE - be7_exch)

    li7_final = li7_exch * (1.0 - gamma_drain)
    be7_final = be7_exch * (1.0 - gamma_drain)
    li_total_final = li7_final + be7_final

    li7_pass = LI_MIN <= li7_final <= LI_MAX
    li_total_pass = LI_MIN <= li_total_final <= LI_MAX

    return {
        "gamma_exch": gamma_exch,
        "gamma_drain": gamma_drain,
        "eta_exch": eta_exch,
        "Li7_exch": li7_exch,
        "Be7_exch": be7_exch,
        "Li7_final": li7_final,
        "Be7_final": be7_final,
        "Li_total_final": li_total_final,
        "Li7_pass": li7_pass,
        "LiTot_pass": li_total_pass,
        "passes_both": li7_pass and li_total_pass,
    }


def grid_values(start: float, stop: float, count: int) -> list[float]:
    if count < 2:
        return [start]
    step = (stop - start) / (count - 1)
    return [round(start + i * step, 12) for i in range(count)]


def write_csv(rows: list[dict[str, float | bool]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "gamma_exch",
        "gamma_drain",
        "eta_exch",
        "Li7_exch",
        "Be7_exch",
        "Li7_final",
        "Be7_final",
        "Li_total_final",
        "Li7_pass",
        "LiTot_pass",
        "passes_both",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot_heatmap(rows: list[dict[str, float | bool]], key: str, output_dir: Path, title: str, ylabel: str) -> str:
    exch_values = sorted({float(row["gamma_exch"]) for row in rows})
    drain_values = sorted({float(row["gamma_drain"]) for row in rows})
    matrix = [[0.0 for _ in drain_values] for _ in exch_values]
    for row in rows:
        i = exch_values.index(float(row["gamma_exch"]))
        j = drain_values.index(float(row["gamma_drain"]))
        matrix[i][j] = float(row[key])

    plt.figure(figsize=(8, 5))
    plt.imshow(matrix, origin="lower", aspect="auto", cmap="viridis", extent=[min(drain_values), max(drain_values), min(exch_values), max(exch_values)])
    plt.colorbar(label=ylabel)
    plt.title(title)
    plt.xlabel("gamma_drain")
    plt.ylabel("gamma_exch")
    path = output_dir / f"{key}_heatmap.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return str(path)


def summarize(rows: list[dict[str, float | bool]], csv_path: Path, plot_paths: list[str], output_dir: Path) -> dict[str, object]:
    both_rows = [row for row in rows if bool(row["passes_both"])]
    if both_rows:
        best_row = min(both_rows, key=lambda row: float(row["Li_total_final"]))
        verdict = "zone_viable_trouvee"
    else:
        best_row = min(rows, key=lambda row: float(row["Li_total_final"]))
        verdict = "zone_viable_absente"

    summary = {
        "suite": "v77e_a7_exchange_drain",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "row_count": len(rows),
        "both_pass_count": len(both_rows),
        "best_row": best_row,
        "csv_path": str(csv_path),
        "plot_paths": plot_paths,
        "output_dir": str(output_dir),
    }
    return summary


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v77e_exchange_drain_summary_{timestamp}.json"
    txt_path = output_dir / f"v77e_exchange_drain_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    best = summary["best_row"]
    lines = [
        "V77E exchange + drain scan summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"row_count: {summary['row_count']}",
        f"both_pass_count: {summary['both_pass_count']}",
        f"best_gamma_exch: {best['gamma_exch']}",
        f"best_gamma_drain: {best['gamma_drain']}",
        f"best_Li7_final: {best['Li7_final']}",
        f"best_Be7_final: {best['Be7_final']}",
        f"best_Li_total_final: {best['Li_total_final']}",
        "",
        "Plots:",
    ]
    for path in summary["plot_paths"]:
        lines.append(f"- {path}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_scan(
    exch_min: float,
    exch_max: float,
    exch_count: int,
    drain_min: float,
    drain_max: float,
    drain_count: int,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77e_a7_exchange_drain"
    plot_dir = result_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    exch_values = grid_values(exch_min, exch_max, exch_count)
    drain_values = grid_values(drain_min, drain_max, drain_count)

    rows: list[dict[str, float | bool]] = []
    for gamma_exch in exch_values:
        for gamma_drain in drain_values:
            rows.append(evaluate_point(gamma_exch, gamma_drain))

    csv_path = result_dir / "v77e_exchange_drain_scan.csv"
    write_csv(rows, csv_path)

    plot_paths = [
        plot_heatmap(rows, "Li7_final", plot_dir, "Li7_final vs exchange/drain", "Li7_final"),
        plot_heatmap(rows, "Be7_final", plot_dir, "Be7_final vs exchange/drain", "Be7_final"),
        plot_heatmap(rows, "Li_total_final", plot_dir, "Li_total_final vs exchange/drain", "Li_total_final"),
    ]

    summary = summarize(rows, csv_path, plot_paths, result_dir)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77E exchange and drain scan.")
    parser.add_argument("--exch-min", type=float, default=0.0, help="Minimum gamma_exch value")
    parser.add_argument("--exch-max", type=float, default=1.0, help="Maximum gamma_exch value")
    parser.add_argument("--exch-count", type=int, default=5, help="Number of gamma_exch sample points")
    parser.add_argument("--drain-min", type=float, default=0.0, help="Minimum gamma_drain value")
    parser.add_argument("--drain-max", type=float, default=0.5, help="Maximum gamma_drain value")
    parser.add_argument("--drain-count", type=int, default=5, help="Number of gamma_drain sample points")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_scan(
        args.exch_min,
        args.exch_max,
        args.exch_count,
        args.drain_min,
        args.drain_max,
        args.drain_count,
        args.output_dir,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()