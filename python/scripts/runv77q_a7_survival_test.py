"""Run the V77Q toy survival test for the A=7 sector.

The model separates Be7 and Li7 explicitly and scans a small parameter grid
over Li7 destruction, Be7-to-Li7 conversion, and an optional environment factor.
The goal is not a realistic BBN fit but a local diagnostic of whether the
Li_total band can widen when survival physics is made explicit.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

from runv77m_validation_plus_readout import load_observations, z_score
from runv80_bbn_scan import workspace_root


DEFAULT_OBSERVATIONS_FILE = Path(__file__).resolve().parents[2] / "data" / "v78h_observations.json"


def linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + step * index for index in range(count)]


def gaussian(time_value: float, center: float, sigma: float) -> float:
    if sigma <= 0:
        return 0.0
    exponent = -((time_value - center) ** 2) / (2.0 * sigma ** 2)
    return math.exp(exponent)


def derivatives(
    state: tuple[float, float],
    time_value: float,
    gamma_burn: float,
    gamma_cap: float,
    gamma_be: float,
    t_bbn: float,
    sigma_bbn: float,
    production_amplitude: float,
) -> tuple[float, float]:
    be7, li7 = state
    production = production_amplitude * gaussian(time_value, t_bbn, sigma_bbn)
    d_be7 = production - gamma_be * be7
    d_li7 = -gamma_burn * li7 + gamma_cap * be7
    return d_be7, d_li7


def rk4_integrate(
    gamma_burn: float,
    gamma_cap: float,
    f_env: float,
    time_grid: list[float],
    t_bbn: float,
    sigma_bbn: float,
    production_amplitude: float,
    gamma_be: float,
    li7_initial: float,
    be7_initial: float,
) -> list[dict[str, float]]:
    effective_burn = gamma_burn * f_env
    effective_cap = gamma_cap * f_env
    be7 = be7_initial
    li7 = li7_initial
    rows: list[dict[str, float]] = []

    for index, current_time in enumerate(time_grid):
        if index > 0:
            previous_time = time_grid[index - 1]
            step = current_time - previous_time
            k1_be, k1_li = derivatives((be7, li7), previous_time, effective_burn, effective_cap, gamma_be, t_bbn, sigma_bbn, production_amplitude)
            k2_be, k2_li = derivatives((be7 + 0.5 * step * k1_be, li7 + 0.5 * step * k1_li), previous_time + 0.5 * step, effective_burn, effective_cap, gamma_be, t_bbn, sigma_bbn, production_amplitude)
            k3_be, k3_li = derivatives((be7 + 0.5 * step * k2_be, li7 + 0.5 * step * k2_li), previous_time + 0.5 * step, effective_burn, effective_cap, gamma_be, t_bbn, sigma_bbn, production_amplitude)
            k4_be, k4_li = derivatives((be7 + step * k3_be, li7 + step * k3_li), current_time, effective_burn, effective_cap, gamma_be, t_bbn, sigma_bbn, production_amplitude)
            be7 += (step / 6.0) * (k1_be + 2.0 * k2_be + 2.0 * k3_be + k4_be)
            li7 += (step / 6.0) * (k1_li + 2.0 * k2_li + 2.0 * k3_li + k4_li)
            be7 = max(be7, 0.0)
            li7 = max(li7, 0.0)

        rows.append(
            {
                "t": current_time,
                "Be7": be7,
                "Li7": li7,
                "Li_total": be7 + li7,
            }
        )

    return rows


def scan_survival_grid(
    gamma_burn_values: list[float],
    gamma_cap_values: list[float],
    f_env_values: list[float],
    observations: dict[str, dict[str, float]],
    time_grid: list[float],
    t_bbn: float,
    sigma_bbn: float,
    production_amplitude: float,
    gamma_be: float,
    li7_initial: float,
    be7_initial: float,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    li_target = observations["Li_total_over_H"]["obs"]
    sigma_li = observations["Li_total_over_H"]["sigma"]

    for gamma_burn in gamma_burn_values:
        for gamma_cap in gamma_cap_values:
            for f_env in f_env_values:
                timeline = rk4_integrate(
                    gamma_burn,
                    gamma_cap,
                    f_env,
                    time_grid,
                    t_bbn,
                    sigma_bbn,
                    production_amplitude,
                    gamma_be,
                    li7_initial,
                    be7_initial,
                )
                final_state = timeline[-1]
                li_total = final_state["Li_total"]
                chi_jouet = ((li_total - li_target) ** 2) / (sigma_li ** 2)
                rows.append(
                    {
                        "Gamma_burn": gamma_burn,
                        "Gamma_cap": gamma_cap,
                        "f_env": f_env,
                        "Be7_final": final_state["Be7"],
                        "Li7_final": final_state["Li7"],
                        "Li_total": li_total,
                        "Li_target": li_target,
                        "sigma_Li": sigma_li,
                        "chi_jouet": chi_jouet,
                        "passes": chi_jouet <= 1.0,
                    }
                )
    return rows


def connected_components_1d(sorted_values: list[float], tol: float = 1e-12) -> int:
    if not sorted_values:
        return 0
    components = 1
    for previous, current in zip(sorted_values, sorted_values[1:]):
        if abs(current - previous) > tol:
            components += 1
    return components


def summarize(rows: list[dict[str, float]]) -> dict[str, object]:
    accepted = [row for row in rows if row["passes"]]
    accepted_burn = sorted({row["Gamma_burn"] for row in accepted})
    accepted_cap = sorted({row["Gamma_cap"] for row in accepted})
    accepted_env = sorted({row["f_env"] for row in accepted})
    best = min(rows, key=lambda row: row["chi_jouet"])
    if not accepted:
        bottleneck = "aucune bande stable"
    elif len(accepted) <= 8:
        bottleneck = "couloir ultra-fin"
    elif len(accepted_burn) <= 2 or len(accepted_cap) <= 2:
        bottleneck = "sensibilité forte aux taux"
    else:
        bottleneck = "bande acceptable encore trop fine"
    return {
        "accepted": accepted,
        "accepted_count": len(accepted),
        "accepted_components_burn": connected_components_1d(accepted_burn),
        "accepted_components_cap": connected_components_1d(accepted_cap),
        "accepted_components_env": connected_components_1d(accepted_env),
        "best_fit_Gamma_burn": best["Gamma_burn"],
        "best_fit_Gamma_cap": best["Gamma_cap"],
        "best_fit_f_env": best["f_env"],
        "best_fit_chi_jouet": best["chi_jouet"],
        "best_fit_Li_total": best["Li_total"],
        "bottleneck": bottleneck,
    }


def write_csv(rows: list[dict[str, float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "Gamma_burn",
        "Gamma_cap",
        "f_env",
        "Be7_final",
        "Li7_final",
        "Li_total",
        "Li_target",
        "sigma_Li",
        "chi_jouet",
        "passes",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot_heatmap(rows: list[dict[str, float]], output_path: Path, title: str) -> str:
    burn_values = unique_sorted(rows, "Gamma_burn")
    cap_values = unique_sorted(rows, "Gamma_cap")
    heatmap = [[math.nan for _ in cap_values] for _ in burn_values]
    for row in rows:
        i = burn_values.index(row["Gamma_burn"])
        j = cap_values.index(row["Gamma_cap"])
        heatmap[i][j] = row["chi_jouet"]

    plt.figure(figsize=(8, 5))
    image = plt.imshow(heatmap, origin="lower", aspect="auto", cmap="plasma", extent=[min(cap_values), max(cap_values), min(burn_values), max(burn_values)])
    plt.colorbar(image, label="chi_jouet")
    plt.xlabel("Gamma_cap")
    plt.ylabel("Gamma_burn")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def unique_sorted(rows: list[dict[str, float]], key: str) -> list[float]:
    return sorted({row[key] for row in rows})


def plot_timeline(sample_timeline: list[dict[str, float]], output_path: Path) -> str:
    times = [row["t"] for row in sample_timeline]
    be7 = [row["Be7"] for row in sample_timeline]
    li7 = [row["Li7"] for row in sample_timeline]
    total = [row["Li_total"] for row in sample_timeline]

    plt.figure(figsize=(8, 5))
    plt.plot(times, be7, linewidth=2, label="Be7")
    plt.plot(times, li7, linewidth=2, label="Li7")
    plt.plot(times, total, linewidth=2, label="Li_total")
    plt.xlabel("t")
    plt.ylabel("abundance / H")
    plt.title("V77Q: timeline jouet A=7")
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def write_report(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_path = output_dir / "V77Q_A7_SURVIVAL_REPORT.txt"
    json_path = output_dir / f"v77q_a7_survival_{summary['timestamp']}.json"
    json_path.write_text(json.dumps({**summary, "txt_path": str(txt_path), "json_path": str(json_path)}, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V77Q A=7 survival report",
        f"timestamp: {summary['timestamp']}",
        f"verdict: {summary['verdict']}",
        f"best_fit_Gamma_burn: {summary['best_fit_Gamma_burn']}",
        f"best_fit_Gamma_cap: {summary['best_fit_Gamma_cap']}",
        f"best_fit_f_env: {summary['best_fit_f_env']}",
        f"best_fit_chi_jouet: {summary['best_fit_chi_jouet']}",
        f"best_fit_Li_total: {summary['best_fit_Li_total']}",
        f"accepted_count: {summary['accepted_count']}",
        f"bottleneck: {summary['bottleneck']}",
        "",
        "output_files:",
    ]
    for key in ["csv_path", "heatmap_path", "timeline_path"]:
        value = summary.get(key)
        if value:
            lines.append(f"- {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return txt_path, json_path


def run_v77q_a7_survival_test(
    output_dir: str | Path | None = None,
    observations_json: str | Path | None = None,
    gamma_burn_min: float = 0.02,
    gamma_burn_max: float = 0.22,
    gamma_burn_points: int = 9,
    gamma_cap_min: float = 0.02,
    gamma_cap_max: float = 0.22,
    gamma_cap_points: int = 9,
    f_env_values: list[float] | None = None,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77q_a7_survival_test"
    result_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = result_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    observations = load_observations(observations_json)
    gamma_burn_values = [round(value, 3) for value in linspace(gamma_burn_min, gamma_burn_max, gamma_burn_points)]
    gamma_cap_values = [round(value, 3) for value in linspace(gamma_cap_min, gamma_cap_max, gamma_cap_points)]
    if f_env_values is None:
        f_env_values = [0.8, 1.0, 1.2]

    time_grid = linspace(0.0, 12.0, 241)
    t_bbn = 4.0
    sigma_bbn = 0.8
    production_amplitude = 0.18
    gamma_be = 0.01
    li7_initial = 0.0
    be7_initial = 0.0

    rows = scan_survival_grid(
        gamma_burn_values,
        gamma_cap_values,
        f_env_values,
        observations,
        time_grid,
        t_bbn,
        sigma_bbn,
        production_amplitude,
        gamma_be,
        li7_initial,
        be7_initial,
    )

    summary = summarize(rows)
    csv_path = result_dir / "v77q_survival_results.csv"
    write_csv(rows, csv_path)

    heatmap_path = plot_heatmap(rows, plot_dir / "v77q_survival_heatmap.png", "V77Q: chi_jouet(Gamma_burn, Gamma_cap)")

    reference_timeline = rk4_integrate(
        summary["best_fit_Gamma_burn"],
        summary["best_fit_Gamma_cap"],
        summary["best_fit_f_env"],
        time_grid,
        t_bbn,
        sigma_bbn,
        production_amplitude,
        gamma_be,
        li7_initial,
        be7_initial,
    )
    timeline_path = plot_timeline(reference_timeline, plot_dir / "v77q_survival_timeline.png")

    verdict = "survival_block_opened_band"
    if summary["accepted_count"] == 0:
        verdict = "survival_block_insufficient"
    elif summary["bottleneck"] == "couloir ultra-fin" or summary["bottleneck"] == "sensibilité forte aux taux":
        verdict = "survival_block_still_narrow"

    result = {
        "suite": "v77q_a7_survival_test",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "grid_size": len(rows),
        "gamma_burn_range": [gamma_burn_min, gamma_burn_max, gamma_burn_points],
        "gamma_cap_range": [gamma_cap_min, gamma_cap_max, gamma_cap_points],
        "f_env_values": f_env_values,
        "verdict": verdict,
        "csv_path": str(csv_path),
        "heatmap_path": str(heatmap_path),
        "timeline_path": str(timeline_path),
        **summary,
    }

    txt_path, json_path = write_report(result, result_dir)
    result["txt_path"] = str(txt_path)
    result["json_path"] = str(json_path)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77Q A=7 survival test.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    parser.add_argument("--observations-json", default=None, help="Optional JSON file overriding the observation windows")
    parser.add_argument("--gamma-burn-min", type=float, default=0.02, help="Minimum Li7 burn rate")
    parser.add_argument("--gamma-burn-max", type=float, default=0.22, help="Maximum Li7 burn rate")
    parser.add_argument("--gamma-burn-points", type=int, default=9, help="Number of Li7 burn grid points")
    parser.add_argument("--gamma-cap-min", type=float, default=0.02, help="Minimum Be7->Li7 capture rate")
    parser.add_argument("--gamma-cap-max", type=float, default=0.22, help="Maximum Be7->Li7 capture rate")
    parser.add_argument("--gamma-cap-points", type=int, default=9, help="Number of capture grid points")
    args = parser.parse_args()

    result = run_v77q_a7_survival_test(
        output_dir=args.output_dir,
        observations_json=args.observations_json,
        gamma_burn_min=args.gamma_burn_min,
        gamma_burn_max=args.gamma_burn_max,
        gamma_burn_points=args.gamma_burn_points,
        gamma_cap_min=args.gamma_cap_min,
        gamma_cap_max=args.gamma_cap_max,
        gamma_cap_points=args.gamma_cap_points,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()