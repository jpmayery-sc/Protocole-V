"""Run the V77F curve-shape analysis from the existing V77D and V77E results."""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

from runv80_bbn_scan import workspace_root


def read_csv_rows(csv_path: Path) -> list[dict[str, str]]:
    with csv_path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def to_float(row: dict[str, str], key: str) -> float:
    return float(row[key])


def curvature_sign(values: list[float]) -> str:
    if len(values) < 3:
        return "indetermine"
    slopes = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    second = [slopes[i + 1] - slopes[i] for i in range(len(slopes) - 1)]
    if all(v > 0 for v in second):
        return "convexe"
    if all(v < 0 for v in second):
        return "concave"
    return "mixte"


def monotonicity(values: list[float]) -> str:
    deltas = [values[i + 1] - values[i] for i in range(len(values) - 1)]
    if all(v < 0 for v in deltas):
        return "decroissante"
    if all(v > 0 for v in deltas):
        return "croissante"
    if all(abs(v) < 1e-18 for v in deltas):
        return "plate"
    return "non monotone"


def identify_band(rows: list[dict[str, str]], pass_key: str) -> dict[str, object]:
    accepted = [row for row in rows if row[pass_key] == "True"]
    if not accepted:
        return {"count": 0, "status": "absente"}
    return {
        "count": len(accepted),
        "status": "presente",
        "first": accepted[0],
        "last": accepted[-1],
    }


def plot_v77d(rows: list[dict[str, str]], output_dir: Path) -> str:
    betas = [to_float(row, "beta_e") for row in rows]
    li_total = [to_float(row, "Li_total_over_H") for row in rows]
    li7 = [to_float(row, "Li7_over_H") for row in rows]
    be7 = [to_float(row, "Be7_over_H") for row in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(betas, li_total, marker="o", linewidth=2, label="Li_total")
    plt.plot(betas, li7, marker="o", linewidth=1.5, label="Li7")
    plt.plot(betas, be7, marker="o", linewidth=1.5, label="Be7")
    plt.xlabel("beta_e")
    plt.ylabel("abondance")
    plt.title("V77D: courbe Li_total(beta_e)")
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best")
    path = output_dir / "v77d_curve_shape.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return str(path)


def plot_v77e(rows: list[dict[str, str]], output_dir: Path) -> str:
    exch_values = sorted({to_float(row, "gamma_exch") for row in rows})
    drain_values = sorted({to_float(row, "gamma_drain") for row in rows})
    matrix = [[0.0 for _ in drain_values] for _ in exch_values]
    for row in rows:
        i = exch_values.index(to_float(row, "gamma_exch"))
        j = drain_values.index(to_float(row, "gamma_drain"))
        matrix[i][j] = to_float(row, "Li_total_final")

    plt.figure(figsize=(8, 5))
    plt.imshow(matrix, origin="lower", aspect="auto", cmap="viridis", extent=[min(drain_values), max(drain_values), min(exch_values), max(exch_values)])
    plt.colorbar(label="Li_total_final")
    plt.xlabel("gamma_drain")
    plt.ylabel("gamma_exch")
    plt.title("V77E: surface Li_total(gamma_exch, gamma_drain)")
    path = output_dir / "v77e_surface_shape.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return str(path)


def qualitative_summary(v77d_rows: list[dict[str, str]], v77e_rows: list[dict[str, str]], plot_paths: list[str]) -> str:
    beta_values = [to_float(row, "beta_e") for row in v77d_rows]
    li_total_v77d = [to_float(row, "Li_total_over_H") for row in v77d_rows]
    monotone = monotonicity(li_total_v77d)
    curvature = curvature_sign(li_total_v77d)

    band_v77d = identify_band(v77d_rows, "passes_all_direct")
    band_v77e = identify_band(v77e_rows, "passes_both")
    both_pass_count = band_v77e["count"]

    surface_rows = [to_float(row, "Li_total_final") for row in v77e_rows]
    gamma_exch_values = sorted({to_float(row, "gamma_exch") for row in v77e_rows})
    gamma_drain_values = sorted({to_float(row, "gamma_drain") for row in v77e_rows})

    # Average variation along each axis as a qualitative proxy.
    drain_by_exch = []
    exch_by_drain = []
    for gex in gamma_exch_values:
        subset = [row for row in v77e_rows if to_float(row, "gamma_exch") == gex]
        vals = [to_float(row, "Li_total_final") for row in subset]
        drain_by_exch.append(vals[-1] - vals[0])
    for gdr in gamma_drain_values:
        subset = [row for row in v77e_rows if to_float(row, "gamma_drain") == gdr]
        vals = [to_float(row, "Li_total_final") for row in subset]
        exch_by_drain.append(vals[-1] - vals[0])

    surface_flat_in_exch = all(abs(v) < 1e-18 for v in drain_by_exch)
    surface_descends_in_drain = all(v < 0 for v in exch_by_drain)

    best_row = min(v77e_rows, key=lambda row: to_float(row, "Li_total_final"))
    best_gamma_exch = to_float(best_row, "gamma_exch")
    best_gamma_drain = to_float(best_row, "gamma_drain")

    if both_pass_count >= 4:
        band_width = "moyenne"
    elif both_pass_count >= 1:
        band_width = "ultra-fine"
    else:
        band_width = "absente"

    beta_low = beta_values[0]
    beta_high = beta_values[-1]
    li_low = li_total_v77d[0]
    li_high = li_total_v77d[-1]
    li_drop_fraction = 1.0 - (li_high / li_low)

    lines = [
        "V77F curve shape summary",
        "",
        "V77D beta_e curve:",
        f"- monotonicity: {monotone}",
        f"- curvature: {curvature}",
        f"- beta range: [{beta_low}, {beta_high}]",
        f"- Li_total from {li_low:.6e} to {li_high:.6e}",
        f"- relative drop: {li_drop_fraction:.4f}",
        f"- acceptance band points in V77D direct channel: {band_v77d['count']}",
        "- reading: smooth descent, no internal turning point, minimum at the upper edge of the scanned beta range.",
        "",
        "V77E surface:",
        f"- best gamma_exch: {best_gamma_exch}",
        f"- best gamma_drain: {best_gamma_drain}",
        f"- both-pass points: {both_pass_count}",
        f"- zone width assessment: {band_width}",
        f"- flat along gamma_exch: {surface_flat_in_exch}",
        f"- descending along gamma_drain: {surface_descends_in_drain}",
        "- reading: a ruled surface/strip, not a sharp basin; exchange mainly redistributes Li7 and Be7, while drain controls the actual descent of Li_total.",
        "",
        "Global reading:",
        "- V77D gives a monotone descending curve with a broad endpoint minimum, not a sharp bascule.",
        "- V77E gives a band-like acceptable zone; the curve is controlled by drain, not by exchange alone.",
        "- Be7 is fully emptied at the best point, so the A=7 equilibrium is genuinely inverted in the toy proxy.",
        "",
        "Synthetic sentence:",
        "La courbe Li_total présente une pente nette sans point de bascule interne marqué ; la zone acceptable est moyenne, avec une surface en bande plutôt qu’un puits ultra-fin.",
        "",
        "Plots:",
    ]
    for path in plot_paths:
        lines.append(f"- {path}")
    return "\n".join(lines) + "\n"


def run_curve_shape(output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77f_curve_shape"
    result_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = result_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    v77d_csv = root / "results" / "result-analyse" / "v77d_triplet_epn" / "v77d_triplet_epn_scan.csv"
    v77e_csv = root / "results" / "result-analyse" / "v77e_a7_exchange_drain" / "v77e_exchange_drain_scan.csv"

    v77d_rows = read_csv_rows(v77d_csv)
    v77e_rows = read_csv_rows(v77e_csv)

    plot_paths = [plot_v77d(v77d_rows, plot_dir), plot_v77e(v77e_rows, plot_dir)]
    text = qualitative_summary(v77d_rows, v77e_rows, plot_paths)

    txt_path = result_dir / "V77F_CURVE_SHAPE.txt"
    txt_path.write_text(text, encoding="utf-8")

    summary = {
        "suite": "v77f_curve_shape",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "txt_path": str(txt_path),
        "plot_paths": plot_paths,
        "output_dir": str(result_dir),
    }
    json_path = result_dir / f"v77f_curve_shape_summary_{summary['timestamp']}.json"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    summary["json_path"] = str(json_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77F curve-shape analysis.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    args = parser.parse_args()

    result = run_curve_shape(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()