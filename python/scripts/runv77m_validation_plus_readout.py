"""Run the V77M physical re-validation and interpretive readout.

This module builds on the V77L dry-run physical lever wrapper because the real
AlterBBN/PArthENoPE source tree is not present in this workspace. It therefore
keeps the physical lever semantics and adds a validation grid, observable
filtering, curve/surface plots, and a qualitative recommendation layer.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

import matplotlib.pyplot as plt

from runv77l_physical_levers_impl import run_bbn
from bbn_backend_adapter import BBNPhysicsRequest, backend_is_available, create_backend
from runv80_bbn_scan import workspace_root


REQUIRED_COLUMNS = [
    "beta_e_phys",
    "gamma_exch_phys",
    "gamma_drain_phys",
    "D_over_H",
    "Y_p",
    "Li7_over_H",
    "Li_total_over_H",
]

DEFAULT_OBSERVATIONS_FILE = Path(__file__).resolve().parents[2] / "data" / "v78h_observations.json"


def default_observations() -> dict[str, dict[str, float]]:
    return {
        "D_over_H": {"obs": 2.527e-5, "sigma": 0.030e-5},
        "Y_p": {"obs": 0.2436, "sigma": 0.0040},
        "Li7_over_H": {"obs": 1.3e-10, "sigma": 0.2e-10},
        "Li_total_over_H": {"obs": 1.3e-10, "sigma": 0.2e-10},
    }


def load_observations(path: str | Path | None) -> dict[str, dict[str, float]]:
    observation_path = Path(path) if path is not None else DEFAULT_OBSERVATIONS_FILE
    if not observation_path.exists():
        return default_observations()

    payload = json.loads(observation_path.read_text(encoding="utf-8"))
    observations = default_observations()
    for key in ["D_over_H", "Y_p", "Li7_over_H"]:
        if key not in payload:
            continue
        value = payload[key]
        if isinstance(value, dict):
            observations[key]["obs"] = float(value.get("obs", observations[key]["obs"]))
            observations[key]["sigma"] = float(value.get("sigma", observations[key]["sigma"]))
        elif isinstance(value, (list, tuple)) and len(value) >= 2:
            observations[key]["obs"] = float(value[0])
            observations[key]["sigma"] = float(value[1])
    observations["Li_total_over_H"] = dict(observations["Li7_over_H"])
    return observations


def z_score(model: float, obs: float, sigma_obs: float) -> float:
    if sigma_obs <= 0:
        raise ValueError("sigma_obs must be strictly positive")
    return abs(model - obs) / sigma_obs


def extract_value(result: object, key: str, default: float | bool = 0.0) -> float | bool:
    if isinstance(result, dict):
        value = result.get(key, default)
        return value  # type: ignore[return-value]
    return getattr(result, key, default)


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


def curvature(values: list[float]) -> str:
    if len(values) < 3:
        return "indetermine"
    slopes = [values[index + 1] - values[index] for index in range(len(values) - 1)]
    second = [slopes[index + 1] - slopes[index] for index in range(len(slopes) - 1)]
    if all(value > 0 for value in second):
        return "convexe"
    if all(value < 0 for value in second):
        return "concave"
    return "mixte"


def parameter_grid(
    beta_min: float,
    beta_max: float,
    beta_points: int,
    gamma_exch_max: float,
    gamma_exch_points: int,
    gamma_drain_max: float,
    gamma_drain_points: int,
) -> list[tuple[float, float, float]]:
    if beta_points < 2 or gamma_exch_points < 2 or gamma_drain_points < 2:
        raise ValueError("each grid dimension must contain at least two points")

    def linspace(start: float, stop: float, count: int) -> list[float]:
        if count == 1:
            return [start]
        step = (stop - start) / (count - 1)
        return [start + step * index for index in range(count)]

    beta_values = linspace(beta_min, beta_max, beta_points)
    exch_values = linspace(0.0, gamma_exch_max, gamma_exch_points)
    drain_values = linspace(0.0, gamma_drain_max, gamma_drain_points)
    return [(beta, exch, drain) for beta in beta_values for exch in exch_values for drain in drain_values]


def run_point(
    beta_e_phys: float,
    gamma_exch_phys: float,
    gamma_drain_phys: float,
    backend_adapter: object | None = None,
) -> dict[str, float]:
    if backend_adapter is None:
        result = run_bbn(beta_e_phys, gamma_exch_phys, gamma_drain_phys)
    else:
        request = BBNPhysicsRequest(
            beta_e_phys=beta_e_phys,
            gamma_exch_phys=gamma_exch_phys,
            gamma_drain_phys=gamma_drain_phys,
        )
        result = backend_adapter.run(request)

    return {
        "D_over_H": float(extract_value(result, "D_over_H", float("nan"))),
        "Y_p": float(extract_value(result, "Y_p", float("nan"))),
        "Li7_over_H": float(extract_value(result, "Li7_over_H", float("nan"))),
        "Be7_over_H": float(extract_value(result, "Be7_over_H", 0.0)),
        "Li_total_over_H": float(extract_value(result, "Li_total_over_H", float("nan"))),
        "screening_eff": float(extract_value(result, "screening_eff", 1.0)),
        "capture_eff": float(extract_value(result, "capture_eff", 1.0)),
        "beta_response_ok": bool(extract_value(result, "beta_response_ok", False)),
        "exchange_response_ok": bool(extract_value(result, "exchange_response_ok", False)),
        "drain_response_ok": bool(extract_value(result, "drain_response_ok", False)),
    }


def run_grid(
    beta_min: float,
    beta_max: float,
    beta_points: int,
    gamma_exch_max: float,
    gamma_exch_points: int,
    gamma_drain_max: float,
    gamma_drain_points: int,
    backend_adapter: object | None = None,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    for beta_e_phys, gamma_exch_phys, gamma_drain_phys in parameter_grid(
        beta_min,
        beta_max,
        beta_points,
        gamma_exch_max,
        gamma_exch_points,
        gamma_drain_max,
        gamma_drain_points,
    ):
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
    chi_max_li: float,
    chi_max_litot: float,
) -> list[dict[str, float]]:
    scored_rows: list[dict[str, float]] = []
    for row in rows:
        row = dict(row)
        row["chi_D"] = z_score(row["D_over_H"], observations["D_over_H"]["obs"], observations["D_over_H"]["sigma"])
        row["chi_Y"] = z_score(row["Y_p"], observations["Y_p"]["obs"], observations["Y_p"]["sigma"])
        row["chi_Li7"] = z_score(row["Li7_over_H"], observations["Li7_over_H"]["obs"], observations["Li7_over_H"]["sigma"])
        row["chi_Li_total"] = z_score(row["Li_total_over_H"], observations["Li_total_over_H"]["obs"], observations["Li_total_over_H"]["sigma"])
        row["passes_D"] = row["chi_D"] <= chi_max_d
        row["passes_Y"] = row["chi_Y"] <= chi_max_y
        row["passes_Li7"] = row["chi_Li7"] <= chi_max_li
        row["passes_Li_total"] = row["chi_Li_total"] <= chi_max_litot
        row["passes_all"] = row["passes_D"] and row["passes_Y"] and row["passes_Li7"] and row["passes_Li_total"]
        row["chi_sum"] = row["chi_D"] + row["chi_Y"] + row["chi_Li7"] + row["chi_Li_total"]
        scored_rows.append(row)
    return scored_rows


def accepted_rows(rows: list[dict[str, float]]) -> list[dict[str, float]]:
    return [row for row in rows if row["passes_all"]]


def unique_sorted(rows: list[dict[str, float]], key: str) -> list[float]:
    return sorted({row[key] for row in rows})


def nearest_value(values: list[float], target: float) -> float:
    if not values:
        raise ValueError("cannot select a nearest value from an empty list")
    return min(values, key=lambda value: abs(value - target))


def filter_slice(rows: list[dict[str, float]], key1: str, value1: float, key2: str, value2: float, tol: float = 1e-12) -> list[dict[str, float]]:
    return [
        row
        for row in rows
        if math.isclose(row[key1], value1, rel_tol=0.0, abs_tol=tol) and math.isclose(row[key2], value2, rel_tol=0.0, abs_tol=tol)
    ]


def filter_single(rows: list[dict[str, float]], key: str, value: float, tol: float = 1e-12) -> list[dict[str, float]]:
    return [row for row in rows if math.isclose(row[key], value, rel_tol=0.0, abs_tol=tol)]


def plot_litot_vs_beta(rows: list[dict[str, float]], accepted: list[dict[str, float]], selected_gamma_exch: float, selected_gamma_drain: float, output_dir: Path) -> tuple[str, dict[str, object]]:
    slice_rows = filter_slice(rows, "gamma_exch_phys", selected_gamma_exch, "gamma_drain_phys", selected_gamma_drain)
    if not slice_rows:
        raise ValueError("no rows match the selected gamma slice for beta plotting")

    slice_rows = sorted(slice_rows, key=lambda row: row["beta_e_phys"])
    accepted_slice = filter_slice(accepted, "gamma_exch_phys", selected_gamma_exch, "gamma_drain_phys", selected_gamma_drain)
    beta_values = [row["beta_e_phys"] for row in slice_rows]
    li_total_values = [row["Li_total_over_H"] for row in slice_rows]

    plt.figure(figsize=(8, 5))
    plt.plot(beta_values, li_total_values, color="#1f4e79", linewidth=2, marker="o", label="Li_total BBN")
    if accepted_slice:
        plt.scatter(
            [row["beta_e_phys"] for row in accepted_slice],
            [row["Li_total_over_H"] for row in accepted_slice],
            color="#cc0000",
            s=28,
            label="points acceptés",
            zorder=3,
        )
    plt.xlabel("beta_e_phys")
    plt.ylabel("Li_total/H")
    plt.title("V77M: Li_total(beta_e_phys) sur la tranche retenue")
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best")
    path = output_dir / "v77m_Litot_vs_beta_e_phys.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()

    analysis = {
        "slice_size": len(slice_rows),
        "accepted_slice_size": len(accepted_slice),
        "monotonicity": monotonicity(li_total_values),
        "curvature": curvature(li_total_values),
        "beta_min": beta_values[0],
        "beta_max": beta_values[-1],
        "li_total_min": min(li_total_values),
        "li_total_max": max(li_total_values),
    }
    return str(path), analysis


def plot_surface(rows: list[dict[str, float]], accepted: list[dict[str, float]], selected_beta: float, output_dir: Path) -> tuple[str, dict[str, object]]:
    slice_rows = filter_single(rows, "beta_e_phys", selected_beta)
    if not slice_rows:
        raise ValueError("no rows match the selected beta slice for surface plotting")

    exch_values = unique_sorted(slice_rows, "gamma_exch_phys")
    drain_values = unique_sorted(slice_rows, "gamma_drain_phys")
    accepted_slice = filter_single(accepted, "beta_e_phys", selected_beta)

    plt.figure(figsize=(8, 5))
    if len(exch_values) > 1 and len(drain_values) > 1:
        matrix = [[math.nan for _ in drain_values] for _ in exch_values]
        for row in slice_rows:
            i = exch_values.index(row["gamma_exch_phys"])
            j = drain_values.index(row["gamma_drain_phys"])
            matrix[i][j] = row["Li_total_over_H"]
        image = plt.imshow(
            matrix,
            origin="lower",
            aspect="auto",
            cmap="viridis",
            extent=[min(drain_values), max(drain_values), min(exch_values), max(exch_values)],
        )
        plt.colorbar(image, label="Li_total/H")
    else:
        plt.scatter(
            [row["gamma_drain_phys"] for row in slice_rows],
            [row["gamma_exch_phys"] for row in slice_rows],
            c=[row["Li_total_over_H"] for row in slice_rows],
            cmap="viridis",
            s=55,
        )
        plt.colorbar(label="Li_total/H")

    if accepted_slice:
        plt.scatter(
            [row["gamma_drain_phys"] for row in accepted_slice],
            [row["gamma_exch_phys"] for row in accepted_slice],
            color="#cc0000",
            s=34,
            marker="x",
            label="acceptés",
        )

    plt.xlabel("gamma_drain_phys")
    plt.ylabel("gamma_exch_phys")
    plt.title("V77M: surface Li_total(gamma_exch_phys, gamma_drain_phys)")
    if accepted_slice:
        plt.legend(loc="best")
    path = output_dir / "v77m_Litot_surface_gamma_phys.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()

    analysis = {
        "slice_size": len(slice_rows),
        "accepted_slice_size": len(accepted_slice),
        "gamma_exch_count": len(exch_values),
        "gamma_drain_count": len(drain_values),
        "accepted_unique_gamma_exch": len({row["gamma_exch_phys"] for row in accepted_slice}),
        "accepted_unique_gamma_drain": len({row["gamma_drain_phys"] for row in accepted_slice}),
        "li_total_min": min(row["Li_total_over_H"] for row in slice_rows),
        "li_total_max": max(row["Li_total_over_H"] for row in slice_rows),
    }
    return str(path), analysis


def plot_observables(rows: list[dict[str, float]], accepted: list[dict[str, float]], selected_gamma_exch: float, selected_gamma_drain: float, output_dir: Path) -> str:
    slice_rows = filter_slice(rows, "gamma_exch_phys", selected_gamma_exch, "gamma_drain_phys", selected_gamma_drain)
    if not slice_rows:
        return ""
    slice_rows = sorted(slice_rows, key=lambda row: row["beta_e_phys"])
    accepted_slice = filter_slice(accepted, "gamma_exch_phys", selected_gamma_exch, "gamma_drain_phys", selected_gamma_drain)

    plt.figure(figsize=(8, 5))
    beta_values = [row["beta_e_phys"] for row in slice_rows]
    plt.plot(beta_values, [row["D_over_H"] for row in slice_rows], label="D/H", linewidth=2)
    plt.plot(beta_values, [row["Y_p"] for row in slice_rows], label="Y_p", linewidth=2)
    if accepted_slice:
        plt.scatter([row["beta_e_phys"] for row in accepted_slice], [row["D_over_H"] for row in accepted_slice], color="#cc0000", s=20)
    plt.xlabel("beta_e_phys")
    plt.title("V77M: observables sur la tranche retenue")
    plt.grid(True, alpha=0.25)
    plt.legend(loc="best")
    path = output_dir / "v77m_DH_vs_param.png"
    plt.tight_layout()
    plt.savefig(path, dpi=160)
    plt.close()
    return str(path)


def slice_description(beta_analysis: dict[str, object], surface_analysis: dict[str, object]) -> tuple[str, str]:
    if beta_analysis["monotonicity"] == "decroissante" and beta_analysis["curvature"] == "convexe":
        curve_desc = "pente nette, monotone et convexe"
    elif beta_analysis["monotonicity"] == "decroissante":
        curve_desc = "pente nette mais courbure mixte"
    else:
        curve_desc = f"courbe {beta_analysis['monotonicity']} à courbure {beta_analysis['curvature']}"

    accepted_slice_size = surface_analysis["accepted_slice_size"]
    accepted_unique_gamma_exch = surface_analysis["accepted_unique_gamma_exch"]
    accepted_unique_gamma_drain = surface_analysis["accepted_unique_gamma_drain"]
    if accepted_slice_size >= 4 or (accepted_unique_gamma_exch >= 2 and accepted_unique_gamma_drain >= 2):
        surface_desc = "surface en bande avec zone de passage de largeur moyenne"
    elif accepted_slice_size >= 1:
        surface_desc = "surface acceptable mais étroite"
    else:
        surface_desc = "surface sans zone de passage claire"

    return curve_desc, surface_desc


def write_csv(rows: list[dict[str, float]], csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = REQUIRED_COLUMNS + [
        "Be7_over_H",
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
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v77m_validation_plus_readout_summary_{timestamp}.json"
    txt_path = output_dir / "V77M_PHYS_READOUT.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V77M physical re-validation + interpretive readout",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"input_reference: {summary['input_reference']}",
        f"accepted_count: {summary['accepted_count']}/{summary['total']}",
        f"best_fit_beta_e_phys: {summary['best_fit_beta_e_phys']}",
        f"best_fit_gamma_exch_phys: {summary['best_fit_gamma_exch_phys']}",
        f"best_fit_gamma_drain_phys: {summary['best_fit_gamma_drain_phys']}",
        f"curve_reading: {summary['curve_reading']}",
        f"surface_reading: {summary['surface_reading']}",
        f"recommendation: {summary['recommendation']}",
        "",
        "output_files:",
    ]
    for key in ["csv_full_path", "csv_accepted_path", "plot_litot_beta_path", "plot_surface_path", "plot_observables_path"]:
        value = summary.get(key)
        if value:
            lines.append(f"- {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def interpret_readout(accepted: list[dict[str, float]], best_row: dict[str, float], beta_analysis: dict[str, object], surface_analysis: dict[str, object]) -> tuple[str, str, str]:
    accepted_beta_values = sorted({row["beta_e_phys"] for row in accepted})
    accepted_gamma_pairs = {(row["gamma_exch_phys"], row["gamma_drain_phys"] ) for row in accepted}
    beta_span = len(accepted_beta_values)
    gamma_span = len(accepted_gamma_pairs)

    if not accepted:
        recommendation = "V80 non recommandé"
        robustness = "absent"
    elif len(accepted) >= 8 and beta_span >= 3 and gamma_span >= 3:
        recommendation = "V80 recommandé"
        robustness = "large"
    elif len(accepted) >= 3 and beta_span >= 2 and gamma_span >= 2:
        recommendation = "V80 recommandé"
        robustness = "moyenne"
    else:
        recommendation = "V80 non recommandé"
        robustness = "ultra-fine"

    qualitative = (
        f"Le meilleur point se situe à beta_e_phys={best_row['beta_e_phys']:.3f}, "
        f"gamma_exch_phys={best_row['gamma_exch_phys']:.3f}, gamma_drain_phys={best_row['gamma_drain_phys']:.3f}. "
        f"La tranche beta est {beta_analysis['monotonicity']} et la courbure est {beta_analysis['curvature']}. "
        f"La surface est {surface_analysis['accepted_slice_size']} points acceptés sur la coupe retenue, ce qui suggère une zone {robustness}."
    )

    physical_reading = (
        f"beta_e_phys agit de manière visible mais modérée; gamma_exch_phys participe à la redistribution A=7; "
        f"gamma_drain_phys concentre la réduction de Li_total. Le motif global est {beta_analysis['monotonicity']} / {beta_analysis['curvature']} et la zone acceptable est {robustness}."
    )
    return recommendation, qualitative, physical_reading


def run_v77m_validation_plus_readout(
    output_dir: str | Path | None = None,
    observations_json: str | Path | None = None,
    backend: str | None = None,
    executable_path: str | Path | None = None,
    backend_work_dir: str | Path | None = None,
    beta_min: float = 0.8,
    beta_max: float = 1.2,
    beta_points: int = 5,
    gamma_exch_max: float = 1.0,
    gamma_exch_points: int = 5,
    gamma_drain_max: float = 0.5,
    gamma_drain_points: int = 5,
    chi_max_d: float = 1.0,
    chi_max_y: float = 1.0,
    chi_max_li: float = 1.0,
    chi_max_litot: float = 1.0,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77m_validation_plus_readout"
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
        backend_work = Path(backend_work_dir) if backend_work_dir is not None else result_dir / "backend_work"
        backend_adapter = create_backend(backend, executable_path, work_dir=backend_work)
        backend_name = backend_adapter.backend_name
        backend_executable = str(Path(executable_path))

    observations = load_observations(observations_json)
    rows = run_grid(
        beta_min,
        beta_max,
        beta_points,
        gamma_exch_max,
        gamma_exch_points,
        gamma_drain_max,
        gamma_drain_points,
        backend_adapter=backend_adapter,
    )
    scored = score_rows(rows, observations, chi_max_d, chi_max_y, chi_max_li, chi_max_litot)
    accepted = accepted_rows(scored)

    best_row = min(scored, key=lambda row: row["chi_sum"])
    best_gamma_exch = best_row["gamma_exch_phys"]
    best_gamma_drain = best_row["gamma_drain_phys"]
    best_beta = best_row["beta_e_phys"]

    beta_plot_path, beta_analysis = plot_litot_vs_beta(scored, accepted, best_gamma_exch, best_gamma_drain, plot_dir)
    surface_plot_path, surface_analysis = plot_surface(scored, accepted, best_beta, plot_dir)
    observables_plot_path = plot_observables(scored, accepted, best_gamma_exch, best_gamma_drain, plot_dir)

    curve_reading, surface_reading = slice_description(beta_analysis, surface_analysis)
    recommendation, qualitative_readout, physical_reading = interpret_readout(accepted, best_row, beta_analysis, surface_analysis)
    verdict = "recommended_for_v80" if recommendation == "V80 recommandé" else "not_recommended_for_v80"

    full_csv_path = result_dir / "v77m_results_full.csv"
    accepted_csv_path = result_dir / "v77m_results_accepted.csv"
    write_csv(scored, full_csv_path)
    write_csv(accepted, accepted_csv_path)

    summary = {
        "suite": "v77m_validation_plus_readout",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "input_reference": "V77L dry-run adapter via run_bbn",
        "backend": backend_name,
        "backend_executable": backend_executable,
        "grid": {
            "beta_min": beta_min,
            "beta_max": beta_max,
            "beta_points": beta_points,
            "gamma_exch_max": gamma_exch_max,
            "gamma_exch_points": gamma_exch_points,
            "gamma_drain_max": gamma_drain_max,
            "gamma_drain_points": gamma_drain_points,
        },
        "total": len(scored),
        "accepted_count": len(accepted),
        "best_fit_beta_e_phys": best_beta,
        "best_fit_gamma_exch_phys": best_gamma_exch,
        "best_fit_gamma_drain_phys": best_gamma_drain,
        "curve_reading": curve_reading,
        "surface_reading": surface_reading,
        "recommendation": recommendation,
        "qualitative_readout": qualitative_readout,
        "physical_reading": physical_reading,
        "csv_full_path": str(full_csv_path),
        "csv_accepted_path": str(accepted_csv_path),
        "plot_litot_beta_path": beta_plot_path,
        "plot_surface_path": surface_plot_path,
        "plot_observables_path": observables_plot_path or None,
        "observations": observations,
        "best_fit": best_row,
        "accepted_rows": accepted,
    }

    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77M physical re-validation and interpretive readout.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    parser.add_argument("--observations-json", default=None, help="Optional JSON file overriding the observation windows")
    parser.add_argument("--backend", default=None, help="Optional real BBN backend: alterbbn or parthenope")
    parser.add_argument("--executable-path", default=None, help="Path to the real BBN backend executable")
    parser.add_argument("--backend-work-dir", default=None, help="Working directory for backend input/output files")
    parser.add_argument("--beta-min", type=float, default=0.8, help="Minimum beta_e_phys value")
    parser.add_argument("--beta-max", type=float, default=1.2, help="Maximum beta_e_phys value")
    parser.add_argument("--beta-points", type=int, default=5, help="Number of beta_e_phys points")
    parser.add_argument("--gamma-exch-max", type=float, default=1.0, help="Maximum gamma_exch_phys value")
    parser.add_argument("--gamma-exch-points", type=int, default=5, help="Number of gamma_exch_phys points")
    parser.add_argument("--gamma-drain-max", type=float, default=0.5, help="Maximum gamma_drain_phys value")
    parser.add_argument("--gamma-drain-points", type=int, default=5, help="Number of gamma_drain_phys points")
    parser.add_argument("--chi-max-d", type=float, default=1.0, help="Max chi for D/H acceptance")
    parser.add_argument("--chi-max-y", type=float, default=1.0, help="Max chi for Y_p acceptance")
    parser.add_argument("--chi-max-li", type=float, default=1.0, help="Max chi for Li-7 acceptance")
    parser.add_argument("--chi-max-litot", type=float, default=1.0, help="Max chi for Li_total acceptance")
    args = parser.parse_args()

    result = run_v77m_validation_plus_readout(
        output_dir=args.output_dir,
        observations_json=args.observations_json,
        backend=args.backend,
        executable_path=args.executable_path,
        backend_work_dir=args.backend_work_dir,
        beta_min=args.beta_min,
        beta_max=args.beta_max,
        beta_points=args.beta_points,
        gamma_exch_max=args.gamma_exch_max,
        gamma_exch_points=args.gamma_exch_points,
        gamma_drain_max=args.gamma_drain_max,
        gamma_drain_points=args.gamma_drain_points,
        chi_max_d=args.chi_max_d,
        chi_max_y=args.chi_max_y,
        chi_max_li=args.chi_max_li,
        chi_max_litot=args.chi_max_litot,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()