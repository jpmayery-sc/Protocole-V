"""Run the V77N stability scan and lithium-focused analysis.

The script reuses the V77M/V77L physical-lever machinery, but narrows the
analysis to lithium-centered stability questions: connected acceptance, Li7
cartography, Li_total cartography, and A=7 flip flags.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

from bbn_backend_adapter import BBNPhysicsRequest, backend_is_available, create_backend
from runv77m_validation_plus_readout import (
    accepted_rows as v77m_accepted_rows,
    filter_single,
    filter_slice,
    load_observations,
    nearest_value,
    run_point,
    unique_sorted,
    z_score,
)
from runv80_bbn_scan import workspace_root


DEFAULT_OBSERVATIONS_FILE = Path(__file__).resolve().parents[2] / "data" / "v78h_observations.json"


def linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + step * index for index in range(count)]


def build_grid(beta_values: list[float], exch_values: list[float], drain_values: list[float]) -> list[tuple[float, float, float]]:
    return [(beta, exch, drain) for beta in beta_values for exch in exch_values for drain in drain_values]


def run_grid(
    beta_values: list[float],
    exch_values: list[float],
    drain_values: list[float],
    backend_adapter: object | None = None,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for beta_e_phys, gamma_exch_phys, gamma_drain_phys in build_grid(beta_values, exch_values, drain_values):
        result = run_point(beta_e_phys, gamma_exch_phys, gamma_drain_phys, backend_adapter)
        row = {
            "beta_e_phys": beta_e_phys,
            "gamma_exch_phys": gamma_exch_phys,
            "gamma_drain_phys": gamma_drain_phys,
            **result,
        }
        rows.append(row)
    return rows


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
        row = dict(row)
        row["chi_D"] = z_score(row["D_over_H"], observations["D_over_H"]["obs"], observations["D_over_H"]["sigma"])
        row["chi_Y"] = z_score(row["Y_p"], observations["Y_p"]["obs"], observations["Y_p"]["sigma"])
        row["chi_Li7"] = z_score(row["Li7_over_H"], observations["Li7_over_H"]["obs"], observations["Li7_over_H"]["sigma"])
        row["chi_Li_total"] = z_score(row["Li_total_over_H"], observations["Li_total_over_H"]["obs"], observations["Li_total_over_H"]["sigma"])
        row["Li7_OK"] = row["chi_Li7"] <= chi_max_li7
        row["Li_total_OK"] = row["chi_Li_total"] <= chi_max_litot
        row["passes_D"] = row["chi_D"] <= chi_max_d
        row["passes_Y"] = row["chi_Y"] <= chi_max_y
        row["A7_flipped"] = bool(row["Be7_over_H"] < 0.2 * row["Li7_over_H"])
        row["ACCEPTED"] = row["passes_D"] and row["passes_Y"] and row["Li7_OK"] and row["Li_total_OK"]
        row["chi_sum"] = row["chi_D"] + row["chi_Y"] + row["chi_Li7"] + row["chi_Li_total"]
        scored.append(row)
    return scored


def write_csv(rows: list[dict[str, float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "beta_e_phys",
        "gamma_exch_phys",
        "gamma_drain_phys",
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
        "Li7_OK",
        "Li_total_OK",
        "A7_flipped",
        "ACCEPTED",
        "chi_sum",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def monotonicity(values: list[float]) -> str:
    if len(values) < 2:
        return "indetermine"
    deltas = [values[index + 1] - values[index] for index in range(len(values) - 1)]
    if all(delta < 0 for delta in deltas):
        return "decroissante"
    if all(delta > 0 for delta in deltas):
        return "croissante"
    if all(abs(delta) < 1e-18 for delta in deltas):
        return "plate"
    return "non monotone"


def connected_components_1d(sorted_values: list[float], tol: float = 1e-12) -> int:
    if not sorted_values:
        return 0
    components = 1
    for previous, current in zip(sorted_values, sorted_values[1:]):
        if abs(current - previous) > tol:
            components += 1
    return components


def plot_li_vs_beta(rows: list[dict[str, float]], accepted: list[dict[str, float]], key: str, selected_gamma_exch: float, selected_gamma_drain: float, output_path: Path, title: str) -> str:
    slice_rows = filter_slice(rows, "gamma_exch_phys", selected_gamma_exch, "gamma_drain_phys", selected_gamma_drain)
    if not slice_rows:
        return ""
    slice_rows = sorted(slice_rows, key=lambda row: row["beta_e_phys"])
    accepted_slice = filter_slice(accepted, "gamma_exch_phys", selected_gamma_exch, "gamma_drain_phys", selected_gamma_drain)
    beta_values = [row["beta_e_phys"] for row in slice_rows]
    li_values = [row[key] for row in slice_rows]

    plt.figure(figsize=(8, 5))
    plt.plot(beta_values, li_values, linewidth=2, marker="o", color="#1f4e79")
    if accepted_slice:
        plt.scatter([row["beta_e_phys"] for row in accepted_slice], [row[key] for row in accepted_slice], color="#cc0000", s=24)
    plt.title(title)
    plt.xlabel("beta_e_phys")
    plt.ylabel("Li/H")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def plot_surface(rows: list[dict[str, float]], accepted: list[dict[str, float]], key: str, selected_beta: float, output_path: Path, title: str) -> str:
    slice_rows = filter_single(rows, "beta_e_phys", selected_beta)
    if not slice_rows:
        return ""
    exch_values = unique_sorted(slice_rows, "gamma_exch_phys")
    drain_values = unique_sorted(slice_rows, "gamma_drain_phys")
    accepted_slice = filter_single(accepted, "beta_e_phys", selected_beta)

    plt.figure(figsize=(8, 5))
    if len(exch_values) > 1 and len(drain_values) > 1:
        matrix = [[math.nan for _ in drain_values] for _ in exch_values]
        for row in slice_rows:
            i = exch_values.index(row["gamma_exch_phys"])
            j = drain_values.index(row["gamma_drain_phys"])
            matrix[i][j] = row[key]
        image = plt.imshow(matrix, origin="lower", aspect="auto", cmap="viridis", extent=[min(drain_values), max(drain_values), min(exch_values), max(exch_values)])
        plt.colorbar(image, label="Li/H")
    else:
        plt.scatter([row["gamma_drain_phys"] for row in slice_rows], [row["gamma_exch_phys"] for row in slice_rows], c=[row[key] for row in slice_rows], cmap="viridis", s=55)
        plt.colorbar(label="Li/H")
    if accepted_slice:
        plt.scatter([row["gamma_drain_phys"] for row in accepted_slice], [row["gamma_exch_phys"] for row in accepted_slice], color="#cc0000", s=34, marker="x")
    plt.xlabel("gamma_drain_phys")
    plt.ylabel("gamma_exch_phys")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def plot_flip_map(rows: list[dict[str, float]], output_path: Path) -> str:
    if not rows:
        return ""
    beta_values = unique_sorted(rows, "beta_e_phys")
    exch_values = unique_sorted(rows, "gamma_exch_phys")
    drain_values = unique_sorted(rows, "gamma_drain_phys")
    matrix = [[0.0 for _ in drain_values] for _ in exch_values]
    for row in rows:
        i = exch_values.index(row["gamma_exch_phys"])
        j = drain_values.index(row["gamma_drain_phys"])
        matrix[i][j] = 1.0 if row["A7_flipped"] else 0.0
    plt.figure(figsize=(8, 5))
    image = plt.imshow(matrix, origin="lower", aspect="auto", cmap="magma", extent=[min(drain_values), max(drain_values), min(exch_values), max(exch_values)])
    plt.colorbar(image, label="A7_flipped")
    plt.xlabel("gamma_drain_phys")
    plt.ylabel("gamma_exch_phys")
    plt.title("V77N: carte de bascule A=7")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def profile_line(rows: list[dict[str, float]], beta_values: list[float], exch_values: list[float], drain_values: list[float], accepted: list[dict[str, float]], output_path: Path) -> str:
    if not accepted:
        return ""
    anchor = min(accepted, key=lambda row: row["chi_sum"])
    beta_line = linspace(min(beta_values), max(beta_values), len(beta_values))
    exch_target = nearest_value(exch_values, anchor["gamma_exch_phys"])
    drain_target = nearest_value(drain_values, anchor["gamma_drain_phys"])
    profile = filter_slice(rows, "gamma_exch_phys", exch_target, "gamma_drain_phys", drain_target)
    profile = sorted(profile, key=lambda row: row["beta_e_phys"])
    if not profile:
        return ""

    plt.figure(figsize=(8, 6))
    beta_axis = [row["beta_e_phys"] for row in profile]
    plt.plot(beta_axis, [row["D_over_H"] for row in profile], label="D/H", linewidth=2)
    plt.plot(beta_axis, [row["Y_p"] for row in profile], label="Y_p", linewidth=2)
    plt.plot(beta_axis, [row["Li7_over_H"] for row in profile], label="Li7/H", linewidth=2)
    plt.plot(beta_axis, [row["Li_total_over_H"] for row in profile], label="Li_total/H", linewidth=2)
    plt.xlabel("beta_e_phys")
    plt.title("V77N: profil lithium-only le long d'une ligne de la zone acceptable")
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best")
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def focus_window(center: float, span: float, step: float, lower_bound: float = 0.0) -> list[float]:
    start = max(lower_bound, center - span)
    stop = center + span
    count = int(round((stop - start) / step)) + 1
    values = [round(start + index * step, 2) for index in range(max(count, 1))]
    return sorted({value for value in values if value >= lower_bound})


def lithium_bottleneck_summary(rows: list[dict[str, float]], accepted: list[dict[str, float]]) -> dict[str, object]:
    if not rows:
        return {
            "dominant_bottleneck": "indetermine",
            "dominant_metric": "indetermine",
            "accepted_components": 0,
            "accepted_count": 0,
            "beta_span": 0,
            "gamma_exch_span": 0,
            "gamma_drain_span": 0,
        }

    accepted_beta = sorted({row["beta_e_phys"] for row in accepted})
    accepted_exch = sorted({row["gamma_exch_phys"] for row in accepted})
    accepted_drain = sorted({row["gamma_drain_phys"] for row in accepted})
    best = min(rows, key=lambda row: row["chi_sum"])

    if not accepted:
        dominant_bottleneck = "aucune zone stable"
        dominant_metric = "chi_Li_total"
    elif len(accepted) <= 8:
        dominant_bottleneck = "couloir ultra-fin"
        dominant_metric = "gamma_drain_phys"
    elif len(accepted_beta) <= 2 and len(accepted_exch) <= 2:
        dominant_bottleneck = "surface étroite en croisement beta/exchange"
        dominant_metric = "beta_e_phys / gamma_exch_phys"
    elif len(accepted_drain) <= 2:
        dominant_bottleneck = "forte sensibilité au drain A=7"
        dominant_metric = "gamma_drain_phys"
    else:
        dominant_bottleneck = "bande acceptable encore trop fine"
        dominant_metric = "Li_total/H"

    return {
        "dominant_bottleneck": dominant_bottleneck,
        "dominant_metric": dominant_metric,
        "accepted_components": connected_components_1d(accepted_beta),
        "accepted_count": len(accepted),
        "beta_span": (accepted_beta[0], accepted_beta[-1]) if accepted_beta else None,
        "gamma_exch_span": (accepted_exch[0], accepted_exch[-1]) if accepted_exch else None,
        "gamma_drain_span": (accepted_drain[0], accepted_drain[-1]) if accepted_drain else None,
        "best_fit_beta_e_phys": best["beta_e_phys"],
        "best_fit_gamma_exch_phys": best["gamma_exch_phys"],
        "best_fit_gamma_drain_phys": best["gamma_drain_phys"],
        "best_fit_chi_sum": best["chi_sum"],
    }


def write_focused_report(summary: dict[str, object], focus: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_path = output_dir / "V77N_FOCUSED_LITHIUM_REPORT.txt"
    json_path = output_dir / f"v77n_focused_decision_{summary['timestamp']}.json"
    payload = {**summary, **{f"focused_{key}": value for key, value in focus.items()}, "txt_path": str(txt_path), "json_path": str(json_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V77N focused lithium report",
        f"timestamp: {summary['timestamp']}",
        f"best_fit_beta_e_phys: {focus['best_fit_beta_e_phys']}",
        f"best_fit_gamma_exch_phys: {focus['best_fit_gamma_exch_phys']}",
        f"best_fit_gamma_drain_phys: {focus['best_fit_gamma_drain_phys']}",
        f"best_fit_chi_sum: {focus['best_fit_chi_sum']}",
        f"accepted_count: {focus['accepted_count']}",
        f"accepted_components: {focus['accepted_components']}",
        f"dominant_bottleneck: {focus['dominant_bottleneck']}",
        f"dominant_metric: {focus['dominant_metric']}",
        f"beta_span: {focus['beta_span']}",
        f"gamma_exch_span: {focus['gamma_exch_span']}",
        f"gamma_drain_span: {focus['gamma_drain_span']}",
        "",
        "Interpretation:",
        "- the accepted set is now centered on the best V77N point and exposes the local bottleneck.",
        "- if gamma_drain_span collapses faster than beta_span and gamma_exch_span, the Li_total window is what pinches the physics.",
        "- if beta_span remains narrow too, the electronic lever is part of the lock, not just a cosmetic correction.",
        "",
        "output_files:",
    ]
    for key in ["csv_focused_path", "plot_focused_li7_beta_path", "plot_focused_litot_beta_path", "plot_focused_li7_surface_path", "plot_focused_litot_surface_path"]:
        value = summary.get(key)
        if value:
            lines.append(f"- {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return txt_path, json_path


def write_report(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_path = output_dir / "V77N_STABILITY_AND_LITHIUM_REPORT.txt"
    json_path = output_dir / f"v77n_decision_{summary['timestamp']}.json"
    payload = {**summary, "txt_path": str(txt_path), "json_path": str(json_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V77N stability and lithium focus report",
        f"timestamp: {summary['timestamp']}",
        f"verdict: {summary['verdict']}",
        f"refined_accepted: {summary['refined_accepted']}",
        f"extended_accepted: {summary['extended_accepted']}",
        f"li7_ok: {summary['li7_ok_count']}",
        f"li_total_ok: {summary['li_total_ok_count']}",
        f"a7_flipped: {summary['a7_flipped_count']}",
        f"robustness: {summary['robustness']}",
        f"li_verdict: {summary['li_verdict']}",
        f"recommendation: {summary['recommendation']}",
        "",
        "output_files:",
    ]
    for key in ["csv_refined_path", "csv_extended_path", "csv_flags_path", "plot_li7_beta_path", "plot_litot_beta_path", "plot_li7_surface_path", "plot_litot_surface_path", "plot_flip_map_path", "plot_profile_path"]:
        value = summary.get(key)
        if value:
            lines.append(f"- {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return txt_path, json_path


def analyse_acceptance(rows: list[dict[str, float]]) -> dict[str, object]:
    accepted = [row for row in rows if row["ACCEPTED"]]
    accepted_beta = sorted({row["beta_e_phys"] for row in accepted})
    accepted_gamma_pairs = {(row["gamma_exch_phys"], row["gamma_drain_phys"]) for row in accepted}
    components = connected_components_1d(accepted_beta)
    a7_flipped_count = sum(1 for row in accepted if row["A7_flipped"])
    robustness = "non fixé"
    if accepted:
        if len(accepted) >= 25 and components == 1 and len(accepted_gamma_pairs) >= 4:
            robustness = "robuste"
        elif len(accepted) >= 10 and components <= 2:
            robustness = "moyenne"
        else:
            robustness = "ultra-fine"
    li_verdict = "non fixé"
    if a7_flipped_count > 0 and robustness == "robuste":
        li_verdict = "Li fixé de façon robuste"
    elif a7_flipped_count > 0 and robustness == "moyenne":
        li_verdict = "Li fixé de façon moyenne"
    elif a7_flipped_count > 0:
        li_verdict = "Li fixé seulement de façon ultra-fine"
    recommendation = "V80 non recommandé"
    if li_verdict in {"Li fixé de façon robuste", "Li fixé de façon moyenne"}:
        recommendation = "V80 recommandé"
    elif li_verdict == "Li fixé seulement de façon ultra-fine":
        recommendation = "V80 à manier avec prudence"
    return {
        "accepted": accepted,
        "accepted_beta": accepted_beta,
        "accepted_gamma_pairs": accepted_gamma_pairs,
        "components": components,
        "a7_flipped_count": a7_flipped_count,
        "robustness": robustness,
        "li_verdict": li_verdict,
        "recommendation": recommendation,
    }


def run_v77n_stability_and_lithium_focus(
    output_dir: str | Path | None = None,
    observations_json: str | Path | None = None,
    backend: str | None = None,
    executable_path: str | Path | None = None,
    backend_work_dir: str | Path | None = None,
    chi_max_d: float = 1.0,
    chi_max_y: float = 1.0,
    chi_max_li7: float = 1.0,
    chi_max_litot: float = 1.0,
    f_threshold: float = 0.2,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77n_stability_and_lithium_focus"
    result_dir.mkdir(parents=True, exist_ok=True)
    plot_dir = result_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)

    backend_adapter = None
    backend_name = None
    backend_executable = None
    if backend is not None:
        if executable_path is None:
            raise ValueError("executable_path is required when backend is provided")
        if not backend_is_available(executable_path):
            raise FileNotFoundError(f"backend executable not available: {executable_path}")
        backend_adapter = create_backend(backend, executable_path, work_dir=backend_work_dir or result_dir / "backend_work")
        backend_name = backend_adapter.backend_name
        backend_executable = str(Path(executable_path))

    observations = load_observations(observations_json)
    beta_refined = [round(value, 2) for value in linspace(1.05, 1.15, 11)]
    exch_refined = [round(value, 2) for value in linspace(0.4, 0.6, 11)]
    drain_refined = [round(value, 2) for value in linspace(0.15, 0.35, 11)]

    beta_extended = [round(value, 2) for value in linspace(0.7, 1.3, 13)]
    exch_extended = [round(value, 2) for value in linspace(0.0, 1.2, 13)]
    drain_extended = [round(value, 2) for value in linspace(0.0, 0.7, 15)]

    refined_rows = run_grid(beta_refined, exch_refined, drain_refined, backend_adapter=backend_adapter)
    extended_rows = run_grid(beta_extended, exch_extended, drain_extended, backend_adapter=backend_adapter)

    refined_scored = score_rows(refined_rows, observations, chi_max_d, chi_max_y, chi_max_li7, chi_max_litot)
    extended_scored = score_rows(extended_rows, observations, chi_max_d, chi_max_y, chi_max_li7, chi_max_litot)

    refined_stats = analyse_acceptance(refined_scored)
    extended_stats = analyse_acceptance(extended_scored)

    refined_accepted = refined_stats["accepted"]
    extended_accepted = extended_stats["accepted"]

    refined_csv_path = result_dir / "v77n_results_refined.csv"
    extended_csv_path = result_dir / "v77n_results_extended.csv"
    flags_csv_path = result_dir / "v77n_results_lithium_flags.csv"
    write_csv(refined_scored, refined_csv_path)
    write_csv(extended_scored, extended_csv_path)
    write_csv(extended_scored, flags_csv_path)

    best_row = min(extended_scored, key=lambda row: row["chi_sum"])
    best_gamma_exch = best_row["gamma_exch_phys"]
    best_gamma_drain = best_row["gamma_drain_phys"]
    best_beta = best_row["beta_e_phys"]

    plot_li7_beta_path = plot_li_vs_beta(extended_scored, extended_accepted, "Li7_over_H", best_gamma_exch, best_gamma_drain, plot_dir / "v77n_Li7_vs_beta_e_phys.png", "V77N: Li7/H(beta_e_phys)")
    plot_litot_beta_path = plot_li_vs_beta(extended_scored, extended_accepted, "Li_total_over_H", best_gamma_exch, best_gamma_drain, plot_dir / "v77n_Litot_vs_beta_e_phys.png", "V77N: Li_total/H(beta_e_phys)")
    plot_li7_surface_path = plot_surface(extended_scored, extended_accepted, "Li7_over_H", best_beta, plot_dir / "v77n_Li7_surface_gamma_phys.png", "V77N: Li7/H(gamma_exch_phys, gamma_drain_phys)")
    plot_litot_surface_path = plot_surface(extended_scored, extended_accepted, "Li_total_over_H", best_beta, plot_dir / "v77n_Litot_surface_gamma_phys.png", "V77N: Li_total/H(gamma_exch_phys, gamma_drain_phys)")
    plot_flip_map_path = plot_flip_map(extended_scored, plot_dir / "v77n_A7_flip_map.png")
    plot_profile_path = profile_line(extended_scored, beta_extended, exch_extended, drain_extended, extended_accepted, plot_dir / "v77n_lithium_profile.png")

    focused_beta = focus_window(best_beta, 0.02, 0.01, lower_bound=0.0)
    focused_exch = focus_window(best_gamma_exch, 0.05, 0.01, lower_bound=0.0)
    focused_drain = focus_window(best_gamma_drain, 0.05, 0.01, lower_bound=0.0)
    focused_rows = run_grid(focused_beta, focused_exch, focused_drain, backend_adapter=backend_adapter)
    focused_scored = score_rows(focused_rows, observations, chi_max_d, chi_max_y, chi_max_li7, chi_max_litot)
    focused_accepted = [row for row in focused_scored if row["ACCEPTED"]]
    focus = lithium_bottleneck_summary(focused_scored, focused_accepted)

    focused_csv_path = result_dir / "v77n_results_focused.csv"
    write_csv(focused_scored, focused_csv_path)

    plot_focused_li7_beta_path = plot_li_vs_beta(focused_scored, focused_accepted, "Li7_over_H", focus["best_fit_gamma_exch_phys"], focus["best_fit_gamma_drain_phys"], plot_dir / "v77n_focused_Li7_vs_beta_e_phys.png", "V77N focused: Li7/H(beta_e_phys)")
    plot_focused_litot_beta_path = plot_li_vs_beta(focused_scored, focused_accepted, "Li_total_over_H", focus["best_fit_gamma_exch_phys"], focus["best_fit_gamma_drain_phys"], plot_dir / "v77n_focused_Litot_vs_beta_e_phys.png", "V77N focused: Li_total/H(beta_e_phys)")
    plot_focused_li7_surface_path = plot_surface(focused_scored, focused_accepted, "Li7_over_H", focus["best_fit_beta_e_phys"], plot_dir / "v77n_focused_Li7_surface_gamma_phys.png", "V77N focused: Li7/H(gamma_exch_phys, gamma_drain_phys)")
    plot_focused_litot_surface_path = plot_surface(focused_scored, focused_accepted, "Li_total_over_H", focus["best_fit_beta_e_phys"], plot_dir / "v77n_focused_Litot_surface_gamma_phys.png", "V77N focused: Li_total/H(gamma_exch_phys, gamma_drain_phys)")

    li7_ok_count = sum(1 for row in extended_scored if row["Li7_OK"])
    li_total_ok_count = sum(1 for row in extended_scored if row["Li_total_OK"])
    a7_flipped_count = sum(1 for row in extended_scored if row["A7_flipped"])

    summary = {
        "suite": "v77n_stability_and_lithium_focus",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "backend": backend_name,
        "backend_executable": backend_executable,
        "refined_total": len(refined_scored),
        "extended_total": len(extended_scored),
        "refined_accepted": len(refined_accepted),
        "extended_accepted": len(extended_accepted),
        "li7_ok_count": li7_ok_count,
        "li_total_ok_count": li_total_ok_count,
        "a7_flipped_count": a7_flipped_count,
        "best_fit_beta_e_phys": best_beta,
        "best_fit_gamma_exch_phys": best_gamma_exch,
        "best_fit_gamma_drain_phys": best_gamma_drain,
        "refined_accepted_components": refined_stats["components"],
        "extended_accepted_components": extended_stats["components"],
        "robustness": extended_stats["robustness"],
        "li_verdict": extended_stats["li_verdict"],
        "recommendation": extended_stats["recommendation"],
        "verdict": "recommended_for_v80" if extended_stats["recommendation"].startswith("V80 recommandé") else "not_recommended_for_v80",
        "csv_refined_path": str(refined_csv_path),
        "csv_extended_path": str(extended_csv_path),
        "csv_flags_path": str(flags_csv_path),
        "plot_li7_beta_path": plot_li7_beta_path,
        "plot_litot_beta_path": plot_litot_beta_path,
        "plot_li7_surface_path": plot_li7_surface_path,
        "plot_litot_surface_path": plot_litot_surface_path,
        "plot_flip_map_path": plot_flip_map_path,
        "plot_profile_path": plot_profile_path or None,
        "csv_focused_path": str(focused_csv_path),
        "plot_focused_li7_beta_path": plot_focused_li7_beta_path,
        "plot_focused_litot_beta_path": plot_focused_litot_beta_path,
        "plot_focused_li7_surface_path": plot_focused_li7_surface_path,
        "plot_focused_litot_surface_path": plot_focused_litot_surface_path,
        "observations": observations,
        "refined_rows": refined_scored,
        "extended_rows": extended_scored,
        "focused_rows": focused_scored,
        "focused_accepted": focused_accepted,
        "focused_bottleneck": focus,
    }

    txt_path, json_path = write_report(summary, result_dir)
    focused_txt_path, focused_json_path = write_focused_report(summary, focus, result_dir)
    summary["txt_path"] = str(txt_path)
    summary["json_path"] = str(json_path)
    summary["focused_txt_path"] = str(focused_txt_path)
    summary["focused_json_path"] = str(focused_json_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77N stability and lithium-focused scan.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    parser.add_argument("--observations-json", default=None, help="Optional JSON file overriding the observation windows")
    parser.add_argument("--backend", default=None, help="Optional real BBN backend: alterbbn or parthenope")
    parser.add_argument("--executable-path", default=None, help="Path to the real BBN backend executable")
    parser.add_argument("--backend-work-dir", default=None, help="Working directory for backend input/output files")
    parser.add_argument("--chi-max-d", type=float, default=1.0, help="Max chi for D/H acceptance")
    parser.add_argument("--chi-max-y", type=float, default=1.0, help="Max chi for Y_p acceptance")
    parser.add_argument("--chi-max-li7", type=float, default=1.0, help="Max chi for Li7 acceptance")
    parser.add_argument("--chi-max-litot", type=float, default=1.0, help="Max chi for Li_total acceptance")
    args = parser.parse_args()

    result = run_v77n_stability_and_lithium_focus(
        output_dir=args.output_dir,
        observations_json=args.observations_json,
        backend=args.backend,
        executable_path=args.executable_path,
        backend_work_dir=args.backend_work_dir,
        chi_max_d=args.chi_max_d,
        chi_max_y=args.chi_max_y,
        chi_max_li7=args.chi_max_li7,
        chi_max_litot=args.chi_max_litot,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
