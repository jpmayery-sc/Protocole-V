"""Run the V77P EM-block projection on the A=7 sector.

This wrapper starts from the V77N/V77O A=7 grid and applies a minimal
electromagnetic projection to Li7, Be7, D/H, and Y_p. It also performs a
small tuning scan around zero EM to check whether a nearby setting is more
favorable than the no-EM baseline.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

from runv77m_validation_plus_readout import load_observations, run_point, z_score
from runv80_bbn_scan import workspace_root


DEFAULT_OBSERVATIONS_FILE = Path(__file__).resolve().parents[2] / "data" / "v78h_observations.json"


def linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + step * index for index in range(count)]


EM_SURFACES = [
    {"name": "S_EM_OFF", "label": "no EM", "B_eff": 0.0, "E_ind": 0.0},
    {"name": "S_EM_SOFT", "label": "EM soft", "B_eff": 0.2, "E_ind": 0.1},
    {"name": "S_EM_STRONG", "label": "EM strong", "B_eff": 0.4, "E_ind": 0.2},
]

EM_TUNING_B_VALUES = [round(value, 2) for value in linspace(0.0, 0.12, 7)]
EM_TUNING_E_VALUES = [round(value, 2) for value in linspace(-0.04, 0.08, 7)]


def build_grid(beta_values: list[float], exch_values: list[float], drain_values: list[float]) -> list[tuple[float, float, float]]:
    return [(beta, exch, drain) for beta in beta_values for exch in exch_values for drain in drain_values]


def run_grid(beta_values: list[float], exch_values: list[float], drain_values: list[float]) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for beta_e_phys, gamma_exch_phys, gamma_drain_phys in build_grid(beta_values, exch_values, drain_values):
        result = run_point(beta_e_phys, gamma_exch_phys, gamma_drain_phys, None)
        rows.append(
            {
                "beta_e_phys": beta_e_phys,
                "gamma_exch_phys": gamma_exch_phys,
                "gamma_drain_phys": gamma_drain_phys,
                **result,
            }
        )
    return rows


def apply_em_projection(row: dict[str, float], b_eff: float, e_ind: float) -> dict[str, float]:
    em_scale = max(0.6, 1.0 - 0.18 * b_eff - 0.12 * e_ind)
    be7_scale = max(0.55, 1.0 - 0.24 * b_eff - 0.16 * e_ind)
    d_scale = 1.0 + 0.008 * b_eff - 0.003 * e_ind
    y_shift = 0.0014 * b_eff - 0.0007 * e_ind
    screening_scale = 1.0 + 0.03 * b_eff
    capture_scale = 1.0 + 0.02 * e_ind

    projected = dict(row)
    projected["B_eff"] = b_eff
    projected["E_ind"] = e_ind
    projected["em_scale"] = em_scale
    projected["be7_scale"] = be7_scale
    projected["D_over_H"] = row["D_over_H"] * d_scale
    projected["Y_p"] = row["Y_p"] + y_shift
    projected["Li7_over_H"] = row["Li7_over_H"] * em_scale
    projected["Be7_over_H"] = row["Be7_over_H"] * be7_scale
    projected["Li_total_over_H"] = projected["Li7_over_H"] + projected["Be7_over_H"]
    projected["screening_eff"] = row.get("screening_eff", 1.0) * screening_scale
    projected["capture_eff"] = row.get("capture_eff", 1.0) * capture_scale
    projected["beta_response_ok"] = bool(row.get("beta_response_ok", False))
    projected["exchange_response_ok"] = bool(row.get("exchange_response_ok", False))
    projected["drain_response_ok"] = bool(row.get("drain_response_ok", False))
    return projected


def score_rows(
    rows: list[dict[str, float]],
    observations: dict[str, dict[str, float]],
    chi_max_d: float,
    chi_max_y: float,
    chi_max_li7: float,
    chi_max_litot: float,
) -> list[dict[str, float]]:
    scored: list[dict[str, float]] = []
    for row in rows:
        projected = dict(row)
        projected["chi_D"] = z_score(projected["D_over_H"], observations["D_over_H"]["obs"], observations["D_over_H"]["sigma"])
        projected["chi_Y"] = z_score(projected["Y_p"], observations["Y_p"]["obs"], observations["Y_p"]["sigma"])
        projected["chi_Li7"] = z_score(projected["Li7_over_H"], observations["Li7_over_H"]["obs"], observations["Li7_over_H"]["sigma"])
        projected["chi_Li_total"] = z_score(projected["Li_total_over_H"], observations["Li_total_over_H"]["obs"], observations["Li_total_over_H"]["sigma"])
        projected["passes_D"] = projected["chi_D"] <= chi_max_d
        projected["passes_Y"] = projected["chi_Y"] <= chi_max_y
        projected["passes_Li7"] = projected["chi_Li7"] <= chi_max_li7
        projected["passes_Li_total"] = projected["chi_Li_total"] <= chi_max_litot
        projected["passes_all"] = projected["passes_D"] and projected["passes_Y"] and projected["passes_Li7"] and projected["passes_Li_total"]
        projected["chi_sum"] = projected["chi_D"] + projected["chi_Y"] + projected["chi_Li7"] + projected["chi_Li_total"]
        projected["em_softness"] = 1.0 / (1.0 + 1.5 * projected["B_eff"] + 1.0 * projected["E_ind"])
        scored.append(projected)
    return scored


def accepted_rows(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    return [row for row in rows if row["passes_all"]]


def unique_sorted(rows: list[dict[str, float]], key: str) -> list[float]:
    return sorted({row[key] for row in rows})


def filter_slice(rows: list[dict[str, float]], key1: str, value1: float, key2: str, value2: float, tol: float = 1e-12) -> list[dict[str, float]]:
    return [
        row
        for row in rows
        if math.isclose(row[key1], value1, rel_tol=0.0, abs_tol=tol) and math.isclose(row[key2], value2, rel_tol=0.0, abs_tol=tol)
    ]


def connected_components_1d(sorted_values: list[float], tol: float = 1e-12) -> int:
    if not sorted_values:
        return 0
    components = 1
    for previous, current in zip(sorted_values, sorted_values[1:]):
        if abs(current - previous) > tol:
            components += 1
    return components


def summarize(rows: list[dict[str, float]]) -> dict[str, object]:
    accepted = accepted_rows(rows)
    accepted_beta = sorted({row["beta_e_phys"] for row in accepted})
    accepted_exch = sorted({row["gamma_exch_phys"] for row in accepted})
    accepted_drain = sorted({row["gamma_drain_phys"] for row in accepted})
    best = min(rows, key=lambda row: row["chi_sum"])
    return {
        "accepted": accepted,
        "accepted_count": len(accepted),
        "accepted_components": connected_components_1d(accepted_beta),
        "beta_span": (accepted_beta[0], accepted_beta[-1]) if accepted_beta else None,
        "gamma_exch_span": (accepted_exch[0], accepted_exch[-1]) if accepted_exch else None,
        "gamma_drain_span": (accepted_drain[0], accepted_drain[-1]) if accepted_drain else None,
        "best_fit_beta_e_phys": best["beta_e_phys"],
        "best_fit_gamma_exch_phys": best["gamma_exch_phys"],
        "best_fit_gamma_drain_phys": best["gamma_drain_phys"],
        "best_fit_B_eff": best["B_eff"],
        "best_fit_E_ind": best["E_ind"],
        "best_fit_chi_sum": best["chi_sum"],
        "best_fit_em_softness": best["em_softness"],
    }


def tune_em_settings(
    base_rows: list[dict[str, float]],
    observations: dict[str, dict[str, float]],
    chi_max_d: float,
    chi_max_y: float,
    chi_max_li7: float,
    chi_max_litot: float,
) -> tuple[list[dict[str, float]], dict[str, object]]:
    tuning_rows: list[dict[str, float]] = []
    for b_eff in EM_TUNING_B_VALUES:
        for e_ind in EM_TUNING_E_VALUES:
            projected_rows = [apply_em_projection(row, b_eff, e_ind) for row in base_rows]
            scored_rows = score_rows(projected_rows, observations, chi_max_d, chi_max_y, chi_max_li7, chi_max_litot)
            summary = summarize(scored_rows)
            tuning_rows.append(
                {
                    "B_eff": b_eff,
                    "E_ind": e_ind,
                    "best_fit_chi_sum": float(summary["best_fit_chi_sum"]),
                    "accepted_count": int(summary["accepted_count"]),
                    "accepted_components": int(summary["accepted_components"]),
                    "best_fit_beta_e_phys": float(summary["best_fit_beta_e_phys"]),
                    "best_fit_gamma_exch_phys": float(summary["best_fit_gamma_exch_phys"]),
                    "best_fit_gamma_drain_phys": float(summary["best_fit_gamma_drain_phys"]),
                    "best_fit_em_softness": float(summary["best_fit_em_softness"]),
                }
            )

    best = min(tuning_rows, key=lambda row: row["best_fit_chi_sum"])
    return tuning_rows, {
        "best_B_eff": best["B_eff"],
        "best_E_ind": best["E_ind"],
        "best_fit_chi_sum": best["best_fit_chi_sum"],
        "best_fit_beta_e_phys": best["best_fit_beta_e_phys"],
        "best_fit_gamma_exch_phys": best["best_fit_gamma_exch_phys"],
        "best_fit_gamma_drain_phys": best["best_fit_gamma_drain_phys"],
        "accepted_count": best["accepted_count"],
        "accepted_components": best["accepted_components"],
        "em_softness": best["best_fit_em_softness"],
    }


def compare_surfaces(surface_summaries: dict[str, dict[str, object]]) -> tuple[str, str]:
    best_chi = {name: float(summary["best_fit_chi_sum"]) for name, summary in surface_summaries.items()}
    if best_chi["S_EM_SOFT"] < best_chi["S_EM_OFF"] or best_chi["S_EM_STRONG"] < best_chi["S_EM_OFF"]:
        return "em_softens_structure", min(best_chi, key=best_chi.get)
    if best_chi["S_EM_SOFT"] == best_chi["S_EM_OFF"] == best_chi["S_EM_STRONG"]:
        return "no_em_effect", "none"
    return "mixed_em_response", min(best_chi, key=best_chi.get)


def write_csv(rows: list[dict[str, float]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def plot_litot_vs_beta(
    rows: list[dict[str, float]],
    accepted: list[dict[str, float]],
    selected_B_eff: float,
    selected_E_ind: float,
    output_path: Path,
    title: str,
) -> str:
    slice_rows = [
        row
        for row in rows
        if math.isclose(row["B_eff"], selected_B_eff, rel_tol=0.0, abs_tol=1e-12)
        and math.isclose(row["E_ind"], selected_E_ind, rel_tol=0.0, abs_tol=1e-12)
    ]
    if not slice_rows:
        return ""
    slice_rows = sorted(slice_rows, key=lambda row: row["beta_e_phys"])
    accepted_slice = filter_slice(accepted, "B_eff", selected_B_eff, "E_ind", selected_E_ind)
    beta_values = [row["beta_e_phys"] for row in slice_rows]
    li_values = [row["Li_total_over_H"] for row in slice_rows]

    plt.figure(figsize=(8, 5))
    plt.plot(beta_values, li_values, linewidth=2, marker="o", color="#1f4e79")
    if accepted_slice:
        plt.scatter([row["beta_e_phys"] for row in accepted_slice], [row["Li_total_over_H"] for row in accepted_slice], color="#cc0000", s=24)
    plt.title(title)
    plt.xlabel("beta_e_phys")
    plt.ylabel("Li_total/H (EM projected)")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def plot_surface(rows: list[dict[str, float]], accepted: list[dict[str, float]], selected_beta: float, output_path: Path, title: str) -> str:
    slice_rows = [row for row in rows if math.isclose(row["beta_e_phys"], selected_beta, rel_tol=0.0, abs_tol=1e-12)]
    if not slice_rows:
        return ""
    exch_values = unique_sorted(slice_rows, "gamma_exch_phys")
    drain_values = unique_sorted(slice_rows, "gamma_drain_phys")
    accepted_slice = [row for row in accepted if math.isclose(row["beta_e_phys"], selected_beta, rel_tol=0.0, abs_tol=1e-12)]

    plt.figure(figsize=(8, 5))
    if len(exch_values) > 1 and len(drain_values) > 1:
        matrix = [[math.nan for _ in drain_values] for _ in exch_values]
        for row in slice_rows:
            i = exch_values.index(row["gamma_exch_phys"])
            j = drain_values.index(row["gamma_drain_phys"])
            matrix[i][j] = row["Li_total_over_H"]
        image = plt.imshow(matrix, origin="lower", aspect="auto", cmap="viridis", extent=[min(drain_values), max(drain_values), min(exch_values), max(exch_values)])
        plt.colorbar(image, label="Li_total/H (EM projected)")
    else:
        plt.scatter([row["gamma_drain_phys"] for row in slice_rows], [row["gamma_exch_phys"] for row in slice_rows], c=[row["Li_total_over_H"] for row in slice_rows], cmap="viridis", s=55)
        plt.colorbar(label="Li_total/H (EM projected)")
    if accepted_slice:
        plt.scatter([row["gamma_drain_phys"] for row in accepted_slice], [row["gamma_exch_phys"] for row in accepted_slice], color="#cc0000", s=34, marker="x")
    plt.xlabel("gamma_drain_phys")
    plt.ylabel("gamma_exch_phys")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def plot_tuning_heatmap(tuning_rows: list[dict[str, float]], tuning_summary: dict[str, object], output_path: Path) -> str:
    b_values = unique_sorted(tuning_rows, "B_eff")
    e_values = unique_sorted(tuning_rows, "E_ind")
    heatmap = [[math.nan for _ in e_values] for _ in b_values]
    for row in tuning_rows:
        i = b_values.index(row["B_eff"])
        j = e_values.index(row["E_ind"])
        heatmap[i][j] = row["best_fit_chi_sum"]

    plt.figure(figsize=(8, 5))
    image = plt.imshow(heatmap, origin="lower", aspect="auto", cmap="magma", extent=[min(e_values), max(e_values), min(b_values), max(b_values)])
    plt.colorbar(image, label="best_fit_chi_sum")
    plt.scatter([tuning_summary["best_E_ind"]], [tuning_summary["best_B_eff"]], color="#00ff66", s=60, marker="x")
    plt.xlabel("E_ind")
    plt.ylabel("B_eff")
    plt.title("V77P: fine EM tuning around zero")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def write_report(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_path = output_dir / "V77P_EM_BLOCK_REPORT.txt"
    json_path = output_dir / f"v77p_em_block_{summary['timestamp']}.json"
    json_path.write_text(json.dumps({**summary, "txt_path": str(txt_path), "json_path": str(json_path)}, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V77P EM block report",
        f"timestamp: {summary['timestamp']}",
        f"verdict: {summary['verdict']}",
        f"best_surface: {summary['best_surface']}",
        f"dominant_surface: {summary['dominant_surface']}",
        f"best_fit_beta_e_phys: {summary['best_fit_beta_e_phys']}",
        f"best_fit_gamma_exch_phys: {summary['best_fit_gamma_exch_phys']}",
        f"best_fit_gamma_drain_phys: {summary['best_fit_gamma_drain_phys']}",
        f"best_tuning_B_eff: {summary['best_tuning_B_eff']}",
        f"best_tuning_E_ind: {summary['best_tuning_E_ind']}",
        f"best_tuning_chi_sum: {summary['best_tuning_chi_sum']}",
        "",
        "surface_summaries:",
    ]
    for surface_name, surface_summary in summary["surface_summaries"].items():
        lines.extend(
            [
                f"- {surface_name}: accepted={surface_summary['accepted_count']}, components={surface_summary['accepted_components']}, best_chi_sum={surface_summary['best_fit_chi_sum']}, softness={surface_summary['best_fit_em_softness']}",
                f"  beta_span={surface_summary['beta_span']}",
                f"  gamma_exch_span={surface_summary['gamma_exch_span']}",
                f"  gamma_drain_span={surface_summary['gamma_drain_span']}",
            ]
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "- compare the no-EM surface with soft and strong EM projections.",
            "- the tuning scan around zero is the cheapest check for a more favorable EM setting.",
            "- if chi_sum drops and the Li_total band broadens, EM is acting like a soft mode.",
            "- if nothing changes materially, the A=7 pinch is still structural.",
            "",
            "output_files:",
        ]
    )
    for key in ["csv_surface_paths", "csv_tuning_path", "plot_surface_paths", "plot_tuning_path"]:
        value = summary.get(key)
        if isinstance(value, list):
            for item in value:
                lines.append(f"- {item}")
        elif value:
            lines.append(f"- {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return txt_path, json_path


def run_v77p_em_block(
    output_dir: str | Path | None = None,
    observations_json: str | Path | None = None,
    chi_max_d: float = 1.0,
    chi_max_y: float = 1.0,
    chi_max_li7: float = 1.0,
    chi_max_litot: float = 1.0,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77p_em_block"
    result_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = result_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    observations = load_observations(observations_json)
    beta_values = [round(value, 2) for value in linspace(0.96, 1.04, 9)]
    exch_values = [round(value, 2) for value in linspace(1.03, 1.15, 7)]
    drain_values = [round(value, 2) for value in linspace(0.56, 0.72, 9)]
    base_rows = run_grid(beta_values, exch_values, drain_values)

    tuning_rows, tuning_summary = tune_em_settings(base_rows, observations, chi_max_d, chi_max_y, chi_max_li7, chi_max_litot)
    tuning_csv_path = result_dir / "v77p_em_tuning_scan.csv"
    write_csv(
        tuning_rows,
        tuning_csv_path,
        ["B_eff", "E_ind", "best_fit_chi_sum", "accepted_count", "accepted_components", "best_fit_beta_e_phys", "best_fit_gamma_exch_phys", "best_fit_gamma_drain_phys", "best_fit_em_softness"],
    )
    tuning_plot_path = plot_tuning_heatmap(tuning_rows, tuning_summary, plot_dir / "v77p_em_tuning_scan_heatmap.png")

    surface_summaries: dict[str, dict[str, object]] = {}
    csv_surface_paths: list[str] = []
    plot_surface_paths: list[str] = []
    scored_by_surface: dict[str, list[dict[str, float]]] = {}

    for surface in EM_SURFACES:
        projected_rows = [apply_em_projection(row, surface["B_eff"], surface["E_ind"]) for row in base_rows]
        scored_rows = score_rows(projected_rows, observations, chi_max_d, chi_max_y, chi_max_li7, chi_max_litot)
        scored_by_surface[surface["name"]] = scored_rows
        surface_summaries[surface["name"]] = summarize(scored_rows)

        csv_path = result_dir / f"v77p_results_{surface['name']}.csv"
        csv_surface_paths.append(str(csv_path))
        write_csv(
            scored_rows,
            csv_path,
            [
                "beta_e_phys",
                "gamma_exch_phys",
                "gamma_drain_phys",
                "B_eff",
                "E_ind",
                "em_scale",
                "be7_scale",
                "D_over_H",
                "Y_p",
                "Li7_over_H",
                "Be7_over_H",
                "Li_total_over_H",
                "screening_eff",
                "capture_eff",
                "beta_response_ok",
                "exchange_response_ok",
                "drain_response_ok",
                "chi_D",
                "chi_Y",
                "chi_Li7",
                "chi_Li_total",
                "passes_D",
                "passes_Y",
                "passes_Li7",
                "passes_Li_total",
                "passes_all",
                "chi_sum",
                "em_softness",
            ],
        )

        best_row = min(scored_rows, key=lambda row: row["chi_sum"])
        accepted = accepted_rows(scored_rows)
        plot_surface_paths.append(
            plot_litot_vs_beta(
                scored_rows,
                accepted,
                surface["B_eff"],
                surface["E_ind"],
                plot_dir / f"v77p_{surface['name']}_Li_total_vs_beta_e_phys.png",
                f"V77P {surface['label']}: Li_total/H(beta_e_phys)",
            )
        )
        plot_surface_paths.append(
            plot_surface(
                scored_rows,
                accepted,
                best_row["beta_e_phys"],
                plot_dir / f"v77p_{surface['name']}_Li_surface_gamma_phys.png",
                f"V77P {surface['label']}: Li_total/H(gamma_exch_phys, gamma_drain_phys)",
            )
        )

    best_surface = min(surface_summaries, key=lambda name: surface_summaries[name]["best_fit_chi_sum"])
    dominant_surface = max(surface_summaries, key=lambda name: surface_summaries[name]["accepted_count"])
    verdict, signal = compare_surfaces(surface_summaries)

    summary = {
        "suite": "v77p_em_block",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "grid_size": len(base_rows),
        "beta_range": [0.96, 1.04, 9],
        "gamma_exch_range": [1.03, 1.15, 7],
        "gamma_drain_range": [0.56, 0.72, 9],
        "best_surface": best_surface,
        "dominant_surface": dominant_surface,
        "verdict": verdict,
        "signal": signal,
        "surface_summaries": surface_summaries,
        "tuning_summary": tuning_summary,
        "csv_surface_paths": csv_surface_paths,
        "csv_tuning_path": str(tuning_csv_path),
        "plot_surface_paths": plot_surface_paths,
        "plot_tuning_path": str(tuning_plot_path),
        "scored_by_surface": scored_by_surface,
        "best_fit_beta_e_phys": surface_summaries[best_surface]["best_fit_beta_e_phys"],
        "best_fit_gamma_exch_phys": surface_summaries[best_surface]["best_fit_gamma_exch_phys"],
        "best_fit_gamma_drain_phys": surface_summaries[best_surface]["best_fit_gamma_drain_phys"],
        "best_tuning_B_eff": tuning_summary["best_B_eff"],
        "best_tuning_E_ind": tuning_summary["best_E_ind"],
        "best_tuning_chi_sum": tuning_summary["best_fit_chi_sum"],
    }

    txt_path, json_path = write_report(summary, result_dir)
    summary["txt_path"] = str(txt_path)
    summary["json_path"] = str(json_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77P EM-block projection for A=7.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    parser.add_argument("--observations-json", default=None, help="Optional JSON file overriding the observation windows")
    parser.add_argument("--chi-max-d", type=float, default=1.0, help="Max chi for D/H acceptance")
    parser.add_argument("--chi-max-y", type=float, default=1.0, help="Max chi for Y_p acceptance")
    parser.add_argument("--chi-max-li7", type=float, default=1.0, help="Max chi for Li7 acceptance")
    parser.add_argument("--chi-max-litot", type=float, default=1.0, help="Max chi for Li_total acceptance")
    args = parser.parse_args()

    result = run_v77p_em_block(
        output_dir=args.output_dir,
        observations_json=args.observations_json,
        chi_max_d=args.chi_max_d,
        chi_max_y=args.chi_max_y,
        chi_max_li7=args.chi_max_li7,
        chi_max_litot=args.chi_max_litot,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()