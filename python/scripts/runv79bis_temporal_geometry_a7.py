"""Run the V77O/V79BIS temporal-geometry exploration for the A=7 sector.

This wrapper reuses the V77L/V77M physical-lever machinery and adds a proxy
timeline plus three observation surfaces:
- S_BBN
- S_capture
- S_proxy_obs

The workspace does not contain a real time-dependent BBN solver, so the
timeline is intentionally explicit and proxy-based: it models the gradual
conversion of Be7 into Li7 and then evaluates the lithium acceptance at the
chosen observation surfaces.
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
from runv77m_validation_plus_readout import accepted_rows as v77m_accepted_rows
from runv77m_validation_plus_readout import filter_slice, load_observations, nearest_value, run_point, unique_sorted, z_score
from runv80_bbn_scan import workspace_root


DEFAULT_OBSERVATIONS_FILE = Path(__file__).resolve().parents[2] / "data" / "v78h_observations.json"

SURFACE_SPECS = [
    {"name": "S_BBN", "label": "S_BBN", "t": 0.0, "tau_capture": 2.5, "be7_weight": 1.0},
    {"name": "S_capture", "label": "S_capture", "t": 1.5, "tau_capture": 2.5, "be7_weight": 0.35},
    {"name": "S_proxy_obs", "label": "S_proxy_obs", "t": 8.0, "tau_capture": 2.5, "be7_weight": 0.0},
]


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


def timeline_state(row: dict[str, float], t: float, tau_capture: float, be7_weight: float) -> dict[str, float]:
    capture_fraction = 1.0 - math.exp(-t / tau_capture) if tau_capture > 0 else 1.0
    li7_t = row["Li7_over_H"] + capture_fraction * row["Be7_over_H"]
    be7_t = row["Be7_over_H"] * (1.0 - capture_fraction)
    li_total_t = li7_t + be7_weight * be7_t
    temperature_proxy = math.exp(-0.45 * t)
    return {
        "t": t,
        "T_proxy": temperature_proxy,
        "capture_fraction": capture_fraction,
        "Li7_over_H": li7_t,
        "Be7_over_H": be7_t,
        "Li_total_over_H": li_total_t,
    }


def make_timeline_rows(rows: list[dict[str, float]], sample_rows: list[tuple[str, dict[str, float]]]) -> list[dict[str, float | str]]:
    timeline_points = [0.0, 0.25, 0.5, 1.0, 2.0, 4.0, 8.0]
    timeline_rows: list[dict[str, float | str]] = []
    for label, row in sample_rows:
        for surface in SURFACE_SPECS:
            for t in timeline_points:
                state = timeline_state(row, t, surface["tau_capture"], surface["be7_weight"])
                timeline_rows.append(
                    {
                        "point_label": label,
                        "beta_e_phys": row["beta_e_phys"],
                        "gamma_exch_phys": row["gamma_exch_phys"],
                        "gamma_drain_phys": row["gamma_drain_phys"],
                        "surface_name": surface["name"],
                        **state,
                    }
                )
    return timeline_rows


def score_surface_rows(
    rows: list[dict[str, float]],
    observations: dict[str, dict[str, float]],
    surface: dict[str, float | str],
    chi_max_d: float,
    chi_max_y: float,
    chi_max_litot: float,
) -> list[dict[str, float]]:
    scored_rows: list[dict[str, float]] = []
    for row in rows:
        surface_state = timeline_state(row, float(surface["t"]), float(surface["tau_capture"]), float(surface["be7_weight"]))
        scored_row = dict(row)
        scored_row["surface_name"] = str(surface["name"])
        scored_row["surface_t"] = float(surface["t"])
        scored_row["surface_weight"] = float(surface["be7_weight"])
        scored_row["surface_capture_fraction"] = surface_state["capture_fraction"]
        scored_row["Li7_surface_over_H"] = surface_state["Li7_over_H"]
        scored_row["Be7_surface_over_H"] = surface_state["Be7_over_H"]
        scored_row["Li_total_surface_over_H"] = surface_state["Li_total_over_H"]
        scored_row["chi_D"] = z_score(scored_row["D_over_H"], observations["D_over_H"]["obs"], observations["D_over_H"]["sigma"])
        scored_row["chi_Y"] = z_score(scored_row["Y_p"], observations["Y_p"]["obs"], observations["Y_p"]["sigma"])
        scored_row["chi_Li_total_surface"] = z_score(
            scored_row["Li_total_surface_over_H"],
            observations["Li_total_over_H"]["obs"],
            observations["Li_total_over_H"]["sigma"],
        )
        scored_row["passes_D"] = scored_row["chi_D"] <= chi_max_d
        scored_row["passes_Y"] = scored_row["chi_Y"] <= chi_max_y
        scored_row["passes_Li_total_surface"] = scored_row["chi_Li_total_surface"] <= chi_max_litot
        scored_row["passes_all"] = scored_row["passes_D"] and scored_row["passes_Y"] and scored_row["passes_Li_total_surface"]
        scored_row["chi_sum"] = scored_row["chi_D"] + scored_row["chi_Y"] + scored_row["chi_Li_total_surface"]
        scored_rows.append(scored_row)
    return scored_rows


def accepted_rows(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    return [row for row in rows if row["passes_all"]]


def connected_components_1d(sorted_values: list[float], tol: float = 1e-12) -> int:
    if not sorted_values:
        return 0
    components = 1
    for previous, current in zip(sorted_values, sorted_values[1:]):
        if abs(current - previous) > tol:
            components += 1
    return components


def summarize_acceptance(rows: list[dict[str, float]]) -> dict[str, object]:
    accepted = accepted_rows(rows)
    accepted_beta = sorted({row["beta_e_phys"] for row in accepted})
    accepted_exch = sorted({row["gamma_exch_phys"] for row in accepted})
    accepted_drain = sorted({row["gamma_drain_phys"] for row in accepted})

    if not accepted:
        bottleneck = "aucune zone stable"
        metric = "chi_Li_total_surface"
    elif len(accepted) <= 8:
        bottleneck = "couloir ultra-fin"
        metric = "gamma_drain_phys"
    elif len(accepted_drain) <= 2:
        bottleneck = "forte sensibilité au drain A=7"
        metric = "gamma_drain_phys"
    elif len(accepted_beta) <= 2 and len(accepted_exch) <= 2:
        bottleneck = "surface étroite en croisement beta/exchange"
        metric = "beta_e_phys / gamma_exch_phys"
    else:
        bottleneck = "bande acceptable encore trop fine"
        metric = "Li_total_surface/H"

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
        "best_fit_chi_sum": best["chi_sum"],
        "dominant_bottleneck": bottleneck,
        "dominant_metric": metric,
    }


def write_csv(rows: list[dict[str, float]], path: Path, fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_timeline_csv(rows: list[dict[str, float | str]], path: Path) -> None:
    fieldnames = [
        "point_label",
        "beta_e_phys",
        "gamma_exch_phys",
        "gamma_drain_phys",
        "surface_name",
        "t",
        "T_proxy",
        "capture_fraction",
        "Li7_over_H",
        "Be7_over_H",
        "Li_total_over_H",
    ]
    write_csv(rows, path, fieldnames)


def plot_litot_vs_beta(
    rows: list[dict[str, float]],
    accepted: list[dict[str, float]],
    selected_gamma_exch: float,
    selected_gamma_drain: float,
    output_path: Path,
    title: str,
) -> str:
    slice_rows = filter_slice(rows, "gamma_exch_phys", selected_gamma_exch, "gamma_drain_phys", selected_gamma_drain)
    if not slice_rows:
        return ""
    slice_rows = sorted(slice_rows, key=lambda row: row["beta_e_phys"])
    accepted_slice = filter_slice(accepted, "gamma_exch_phys", selected_gamma_exch, "gamma_drain_phys", selected_gamma_drain)
    beta_values = [row["beta_e_phys"] for row in slice_rows]
    li_values = [row["Li_total_surface_over_H"] for row in slice_rows]

    plt.figure(figsize=(8, 5))
    plt.plot(beta_values, li_values, linewidth=2, marker="o", color="#1f4e79")
    if accepted_slice:
        plt.scatter(
            [row["beta_e_phys"] for row in accepted_slice],
            [row["Li_total_surface_over_H"] for row in accepted_slice],
            color="#cc0000",
            s=24,
        )
    plt.title(title)
    plt.xlabel("beta_e_phys")
    plt.ylabel("Li_total_surface/H")
    plt.grid(True, alpha=0.25)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def plot_surface(
    rows: list[dict[str, float]],
    accepted: list[dict[str, float]],
    selected_beta: float,
    output_path: Path,
    title: str,
) -> str:
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
            matrix[i][j] = row["Li_total_surface_over_H"]
        image = plt.imshow(matrix, origin="lower", aspect="auto", cmap="viridis", extent=[min(drain_values), max(drain_values), min(exch_values), max(exch_values)])
        plt.colorbar(image, label="Li_total_surface/H")
    else:
        plt.scatter([row["gamma_drain_phys"] for row in slice_rows], [row["gamma_exch_phys"] for row in slice_rows], c=[row["Li_total_surface_over_H"] for row in slice_rows], cmap="viridis", s=55)
        plt.colorbar(label="Li_total_surface/H")
    if accepted_slice:
        plt.scatter([row["gamma_drain_phys"] for row in accepted_slice], [row["gamma_exch_phys"] for row in accepted_slice], color="#cc0000", s=34, marker="x")
    plt.xlabel("gamma_drain_phys")
    plt.ylabel("gamma_exch_phys")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)


def write_report(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_path = output_dir / "V79BIS_TEMPORAL_GEOMETRY_REPORT.txt"
    json_path = output_dir / f"v79bis_temporal_geometry_{summary['timestamp']}.json"
    json_path.write_text(json.dumps({**summary, "txt_path": str(txt_path), "json_path": str(json_path)}, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V79BIS temporal geometry report",
        f"timestamp: {summary['timestamp']}",
        f"verdict: {summary['verdict']}",
        f"best_fit_beta_e_phys: {summary['best_fit_beta_e_phys']}",
        f"best_fit_gamma_exch_phys: {summary['best_fit_gamma_exch_phys']}",
        f"best_fit_gamma_drain_phys: {summary['best_fit_gamma_drain_phys']}",
        f"surface_verdict: {summary['surface_verdict']}",
        f"dominant_surface: {summary['dominant_surface']}",
        "",
        "surface_summaries:",
    ]
    for surface_name, surface_summary in summary["surface_summaries"].items():
        lines.extend(
            [
                f"- {surface_name}: accepted={surface_summary['accepted_count']}, components={surface_summary['accepted_components']}, bottleneck={surface_summary['dominant_bottleneck']}, metric={surface_summary['dominant_metric']}",
                f"  beta_span={surface_summary['beta_span']}",
                f"  gamma_exch_span={surface_summary['gamma_exch_span']}",
                f"  gamma_drain_span={surface_summary['gamma_drain_span']}",
            ]
        )
    lines.extend(
        [
            "",
            "Interpretation:",
            "- S_BBN keeps the standard BBN counting of Li7 + Be7.",
            "- S_capture and S_proxy_obs probe whether the Li band is sensitive to the observation surface in time.",
            "- if the accepted band expands at later surfaces, the pinch is temporal-geometric rather than purely structural.",
            "",
            "output_files:",
        ]
    )
    for key in ["csv_timeline_path", "csv_surface_paths", "plot_surface_band_paths"]:
        value = summary.get(key)
        if isinstance(value, list):
            for item in value:
                lines.append(f"- {item}")
        elif value:
            lines.append(f"- {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return txt_path, json_path


def compare_surfaces(surface_summaries: dict[str, dict[str, object]]) -> tuple[str, str]:
    accepted_counts = {name: int(summary["accepted_count"]) for name, summary in surface_summaries.items()}
    if accepted_counts["S_capture"] > accepted_counts["S_BBN"] or accepted_counts["S_proxy_obs"] > accepted_counts["S_BBN"]:
        return "temporal_geometry_opened_band", "S_capture or S_proxy_obs"
    if accepted_counts["S_BBN"] == accepted_counts["S_capture"] == accepted_counts["S_proxy_obs"]:
        return "structural_pinch_persists", "none"
    return "mixed_surface_effect", max(accepted_counts, key=accepted_counts.get)


def run_v79bis_temporal_geometry_a7(
    output_dir: str | Path | None = None,
    observations_json: str | Path | None = None,
    backend: str | None = None,
    executable_path: str | Path | None = None,
    backend_work_dir: str | Path | None = None,
    chi_max_d: float = 1.0,
    chi_max_y: float = 1.0,
    chi_max_litot: float = 1.0,
    beta_min: float = 0.96,
    beta_max: float = 1.04,
    beta_points: int = 9,
    gamma_exch_min: float = 1.03,
    gamma_exch_max: float = 1.15,
    gamma_exch_points: int = 7,
    gamma_drain_min: float = 0.56,
    gamma_drain_max: float = 0.72,
    gamma_drain_points: int = 9,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v79bis_temporal_geometry_a7"
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

    beta_values = [round(value, 2) for value in linspace(beta_min, beta_max, beta_points)]
    exch_values = [round(value, 2) for value in linspace(gamma_exch_min, gamma_exch_max, gamma_exch_points)]
    drain_values = [round(value, 2) for value in linspace(gamma_drain_min, gamma_drain_max, gamma_drain_points)]

    raw_rows = run_grid(beta_values, exch_values, drain_values, backend_adapter=backend_adapter)
    scored_by_surface: dict[str, list[dict[str, float]]] = {}
    surface_summaries: dict[str, dict[str, object]] = {}
    csv_surface_paths: list[str] = []
    plot_surface_band_paths: list[str] = []

    for surface in SURFACE_SPECS:
        scored_rows = score_surface_rows(raw_rows, observations, surface, chi_max_d, chi_max_y, chi_max_litot)
        summary = summarize_acceptance(scored_rows)
        scored_by_surface[str(surface["name"])] = scored_rows
        surface_summaries[str(surface["name"])] = summary

        csv_path = result_dir / f"v79bis_results_{surface['name']}.csv"
        csv_surface_paths.append(str(csv_path))
        write_csv(
            scored_rows,
            csv_path,
            [
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
                "surface_name",
                "surface_t",
                "surface_weight",
                "surface_capture_fraction",
                "Li7_surface_over_H",
                "Be7_surface_over_H",
                "Li_total_surface_over_H",
                "chi_D",
                "chi_Y",
                "chi_Li_total_surface",
                "passes_D",
                "passes_Y",
                "passes_Li_total_surface",
                "passes_all",
                "chi_sum",
            ],
        )

        best_row = min(scored_rows, key=lambda row: row["chi_sum"])
        accepted = accepted_rows(scored_rows)
        beta_anchor = best_row["beta_e_phys"]
        exch_anchor = best_row["gamma_exch_phys"]
        drain_anchor = best_row["gamma_drain_phys"]
        plot_surface_band_paths.append(
            plot_litot_vs_beta(
                scored_rows,
                accepted,
                exch_anchor,
                drain_anchor,
                plot_dir / f"v79bis_{surface['name']}_Litot_vs_beta_e_phys.png",
                f"V79BIS {surface['name']}: Li_total_surface/H(beta_e_phys)",
            )
        )
        plot_surface_band_paths.append(
            plot_surface(
                scored_rows,
                accepted,
                beta_anchor,
                plot_dir / f"v79bis_{surface['name']}_Li_surface_gamma_phys.png",
                f"V79BIS {surface['name']}: Li_total_surface/H(gamma_exch_phys, gamma_drain_phys)",
            )
        )

    best_surface_name = min(surface_summaries, key=lambda name: surface_summaries[name]["best_fit_chi_sum"])
    dominant_surface = max(surface_summaries, key=lambda name: surface_summaries[name]["accepted_count"])
    surface_verdict, surface_signal = compare_surfaces(surface_summaries)

    best_scored_rows = scored_by_surface[best_surface_name]
    best_row_overall = min(best_scored_rows, key=lambda row: row["chi_sum"])
    sample_rows: list[tuple[str, dict[str, float]]] = [("best_overall", best_row_overall)]
    best_accepted = accepted_rows(best_scored_rows)
    if best_accepted:
        sample_rows.append(("best_accepted", min(best_accepted, key=lambda row: row["chi_sum"])))
    if best_scored_rows:
        sample_rows.append(("worst_case", max(best_scored_rows, key=lambda row: row["chi_sum"])))

    timeline_rows = make_timeline_rows(raw_rows, sample_rows)
    timeline_csv_path = result_dir / "v79bis_timeline_a7.csv"
    write_timeline_csv(timeline_rows, timeline_csv_path)

    timeline_plot_path = plot_dir / "v79bis_Li7_Be7_Litot_vs_t.png"
    plt.figure(figsize=(8, 5))
    for label, row in sample_rows:
        t_values = [entry["t"] for entry in timeline_rows if entry["point_label"] == label and entry["surface_name"] == "S_BBN"]
        li7_values = [entry["Li7_over_H"] for entry in timeline_rows if entry["point_label"] == label and entry["surface_name"] == "S_BBN"]
        be7_values = [entry["Be7_over_H"] for entry in timeline_rows if entry["point_label"] == label and entry["surface_name"] == "S_BBN"]
        litot_values = [entry["Li_total_over_H"] for entry in timeline_rows if entry["point_label"] == label and entry["surface_name"] == "S_BBN"]
        plt.plot(t_values, li7_values, marker="o", linewidth=1.8, label=f"{label} Li7/H")
        plt.plot(t_values, be7_values, marker="s", linewidth=1.8, linestyle="--", label=f"{label} Be7/H")
        plt.plot(t_values, litot_values, marker="^", linewidth=1.8, linestyle=":", label=f"{label} Li_total/H")
    plt.xlabel("t (proxy)")
    plt.ylabel("abundance / H")
    plt.title("V79BIS: timeline proxy du secteur A=7")
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best", fontsize=8)
    plt.tight_layout()
    plt.savefig(timeline_plot_path, dpi=160)
    plt.close()

    summary = {
        "suite": "v79bis_temporal_geometry_a7",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "backend": backend_name,
        "backend_executable": backend_executable,
        "grid_size": len(raw_rows),
        "beta_range": [beta_min, beta_max, beta_points],
        "gamma_exch_range": [gamma_exch_min, gamma_exch_max, gamma_exch_points],
        "gamma_drain_range": [gamma_drain_min, gamma_drain_max, gamma_drain_points],
        "best_fit_beta_e_phys": best_row_overall["beta_e_phys"],
        "best_fit_gamma_exch_phys": best_row_overall["gamma_exch_phys"],
        "best_fit_gamma_drain_phys": best_row_overall["gamma_drain_phys"],
        "best_surface_name": best_surface_name,
        "surface_verdict": surface_verdict,
        "surface_signal": surface_signal,
        "dominant_surface": dominant_surface,
        "surface_summaries": surface_summaries,
        "csv_timeline_path": str(timeline_csv_path),
        "csv_surface_paths": csv_surface_paths,
        "plot_timeline_path": str(timeline_plot_path),
        "plot_surface_band_paths": plot_surface_band_paths,
        "raw_rows": raw_rows,
        "scored_by_surface": scored_by_surface,
        "verdict": "temporal_geometry_opened_band" if surface_verdict == "temporal_geometry_opened_band" else "structural_pinch_persists" if surface_verdict == "structural_pinch_persists" else "mixed_surface_effect",
    }

    txt_path, json_path = write_report(summary, result_dir)
    summary["txt_path"] = str(txt_path)
    summary["json_path"] = str(json_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V79BIS temporal-geometry A=7 scan.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    parser.add_argument("--observations-json", default=None, help="Optional JSON file overriding the observation windows")
    parser.add_argument("--backend", default=None, help="Optional real BBN backend: alterbbn or parthenope")
    parser.add_argument("--executable-path", default=None, help="Path to the real BBN backend executable")
    parser.add_argument("--backend-work-dir", default=None, help="Working directory for backend input/output files")
    parser.add_argument("--chi-max-d", type=float, default=1.0, help="Max chi for D/H acceptance")
    parser.add_argument("--chi-max-y", type=float, default=1.0, help="Max chi for Y_p acceptance")
    parser.add_argument("--chi-max-litot", type=float, default=1.0, help="Max chi for surface lithium acceptance")
    parser.add_argument("--beta-min", type=float, default=0.96, help="Minimum beta_e_phys value")
    parser.add_argument("--beta-max", type=float, default=1.04, help="Maximum beta_e_phys value")
    parser.add_argument("--beta-points", type=int, default=9, help="Number of beta grid points")
    parser.add_argument("--gamma-exch-min", type=float, default=1.03, help="Minimum gamma_exch_phys value")
    parser.add_argument("--gamma-exch-max", type=float, default=1.15, help="Maximum gamma_exch_phys value")
    parser.add_argument("--gamma-exch-points", type=int, default=7, help="Number of gamma_exch grid points")
    parser.add_argument("--gamma-drain-min", type=float, default=0.56, help="Minimum gamma_drain_phys value")
    parser.add_argument("--gamma-drain-max", type=float, default=0.72, help="Maximum gamma_drain_phys value")
    parser.add_argument("--gamma-drain-points", type=int, default=9, help="Number of gamma_drain grid points")
    args = parser.parse_args()

    result = run_v79bis_temporal_geometry_a7(
        output_dir=args.output_dir,
        observations_json=args.observations_json,
        backend=args.backend,
        executable_path=args.executable_path,
        backend_work_dir=args.backend_work_dir,
        chi_max_d=args.chi_max_d,
        chi_max_y=args.chi_max_y,
        chi_max_litot=args.chi_max_litot,
        beta_min=args.beta_min,
        beta_max=args.beta_max,
        beta_points=args.beta_points,
        gamma_exch_min=args.gamma_exch_min,
        gamma_exch_max=args.gamma_exch_max,
        gamma_exch_points=args.gamma_exch_points,
        gamma_drain_min=args.gamma_drain_min,
        gamma_drain_max=args.gamma_drain_max,
        gamma_drain_points=args.gamma_drain_points,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()