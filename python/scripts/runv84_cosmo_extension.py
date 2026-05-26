"""Run the V84 toy cosmology extension for the fixed epsilon band.

This script is intentionally phenomenological: it uses the V81-V83 epsilon
calibration as a fixed input, then projects it onto a simple cosmological toy
model for H(z), distances, growth, and CMB distance consistency.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path

from runv82_global_confrontation import delta_em_from_epsilon, pi_n, g_eff, f_temps, workspace_root


def linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + step * index for index in range(count)]


def hubble_standard(z: float, h0: float, omega_m: float, omega_r: float, omega_l: float) -> float:
    return h0 * math.sqrt(max(0.0, omega_r * (1.0 + z) ** 4 + omega_m * (1.0 + z) ** 3 + omega_l))


def toy_growth_rate(z: float, omega_m: float, g_eff_cosmo: float) -> float:
    gamma = 0.55 - 0.08 * (g_eff_cosmo - 1.0)
    omega_m_z = omega_m * (1.0 + z) ** 3 / max(1.0e-12, omega_m * (1.0 + z) ** 3 + (1.0 - omega_m))
    return omega_m_z ** gamma


def toy_chi2_component(model: float, target: float, sigma: float) -> float:
    return ((model - target) / sigma) ** 2


def comoving_distance(z: float, h0: float, omega_m: float, omega_r: float, omega_l: float, g_eff_cosmo: float, f_temps_cosmo: float) -> float:
    steps = 200
    dz = z / steps if steps > 0 else 0.0
    integral = 0.0
    for index in range(steps):
        z_i = (index + 0.5) * dz
        h_i = hubble_standard(z_i, h0, omega_m, omega_r, omega_l)
        h_i *= math.sqrt(g_eff_cosmo) / max(1.0e-12, f_temps_cosmo)
        integral += 1.0 / max(h_i, 1.0e-12)
    c_km_s = 299792.458
    return c_km_s * dz * integral


def angular_diameter_distance(z: float, h0: float, omega_m: float, omega_r: float, omega_l: float, g_eff_cosmo: float, f_temps_cosmo: float) -> float:
    return comoving_distance(z, h0, omega_m, omega_r, omega_l, g_eff_cosmo, f_temps_cosmo) / (1.0 + z)


def luminosity_distance(z: float, h0: float, omega_m: float, omega_r: float, omega_l: float, g_eff_cosmo: float, f_temps_cosmo: float) -> float:
    return comoving_distance(z, h0, omega_m, omega_r, omega_l, g_eff_cosmo, f_temps_cosmo) * (1.0 + z)


def scan_epsilon(
    epsilon_values: list[float],
    pi_cosmo_values: list[float],
    rho_lab: float,
    rho_cosmo: float,
    h0: float,
    omega_m: float,
    omega_l: float,
    omega_r: float,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    z_values = [0.0, 0.5, 1.0, 2.0]
    z_growth_values = [0.0, 0.5, 1.0]
    z_rec = 1100.0

    for epsilon in epsilon_values:
        delta_em = delta_em_from_epsilon(epsilon, 1.0)
        for pi_cosmo in pi_cosmo_values:
            g_lab = g_eff(epsilon, pi_n(epsilon, rho_lab, 1.0 / abs(-0.0069)), 8.0)
            f_lab = f_temps(epsilon, pi_n(epsilon, rho_lab, 1.0 / abs(-0.0069)), 6.0)
            g_cosmo = 1.0 + 12.0 * abs(epsilon) * pi_cosmo
            f_cosmo = 1.0 / (1.0 + 9.0 * abs(epsilon) * pi_cosmo)

            h_ratios = []
            da_values = []
            dl_values = []
            da_ref_values = []
            dl_ref_values = []
            for z in z_values:
                h_ref = hubble_standard(z, h0, omega_m, omega_r, omega_l)
                h_model = h_ref * math.sqrt(g_cosmo) / max(1.0e-12, f_cosmo)
                h_ratios.append(h_model / max(h_ref, 1.0e-12))
                da_values.append(angular_diameter_distance(z, h0, omega_m, omega_r, omega_l, g_cosmo, f_cosmo))
                dl_values.append(luminosity_distance(z, h0, omega_m, omega_r, omega_l, g_cosmo, f_cosmo))
                da_ref_values.append(angular_diameter_distance(z, h0, omega_m, omega_r, omega_l, 1.0, 1.0))
                dl_ref_values.append(luminosity_distance(z, h0, omega_m, omega_r, omega_l, 1.0, 1.0))

            growth_values = [toy_growth_rate(z, omega_m, g_cosmo) for z in z_growth_values]
            da_rec = angular_diameter_distance(z_rec, h0, omega_m, omega_r, omega_l, g_cosmo, f_cosmo)
            first_peak_shift = (1.0 / max(f_cosmo, 1.0e-12)) - 1.0
            omega_m_eff = omega_m * g_cosmo / max(f_cosmo, 1.0e-12)

            chi_sn = sum(toy_chi2_component(ratio, 1.0, 0.03) for ratio in h_ratios)
            chi_bao = sum(
                toy_chi2_component(model / max(reference, 1.0e-12), 1.0, 0.03)
                for model, reference in zip(da_values, da_ref_values)
            ) + sum(
                toy_chi2_component(model / max(reference, 1.0e-12), 1.0, 0.03)
                for model, reference in zip(dl_values, dl_ref_values)
            )
            chi_cmb = toy_chi2_component(da_rec, 12.5, 0.9) + toy_chi2_component(first_peak_shift, 0.0, 0.02)
            chi_growth = sum(toy_chi2_component(value, 0.5, 0.08) for value in growth_values)
            chi_total = chi_sn + chi_bao + chi_cmb + chi_growth

            row = {
                "epsilon": epsilon,
                "delta_em": delta_em,
                "pi_cosmo": pi_cosmo,
                "G_eff_cosmo": g_cosmo,
                "F_temps_cosmo": f_cosmo,
                "omega_m_eff": omega_m_eff,
                "H_ratio_z0": h_ratios[0],
                "H_ratio_z05": h_ratios[1],
                "H_ratio_z1": h_ratios[2],
                "H_ratio_z2": h_ratios[3],
                "DA_rec": da_rec,
                "DL_z0_5": dl_values[1],
                "DL_z1": dl_values[2],
                "f_sigma8_proxy_z0": growth_values[0],
                "f_sigma8_proxy_z05": growth_values[1],
                "f_sigma8_proxy_z1": growth_values[2],
                "first_peak_shift": first_peak_shift,
                "chi_sn": chi_sn,
                "chi_bao": chi_bao,
                "chi_cmb": chi_cmb,
                "chi_growth": chi_growth,
                "chi_total": chi_total,
            }
            row["passes_bbn"] = -0.008 <= delta_em <= -0.0059
            row["passes_cosmo"] = chi_total <= 20.0 and 0.95 <= h_ratios[0] <= 1.05 and 0.98 <= f_cosmo <= 1.02
            row["passes_all"] = row["passes_bbn"] and row["passes_cosmo"]
            rows.append(row)
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
    accepted = [row for row in rows if row["passes_all"]]
    accepted_eps = sorted({row["epsilon"] for row in accepted})
    accepted_pi = sorted({row["pi_cosmo"] for row in accepted})
    best = min(rows, key=lambda row: row["chi_total"])

    if not accepted:
        verdict = "cosmo_rupture"
    elif len(accepted) == len(rows):
        verdict = "cosmo_band_confirmed"
    else:
        verdict = "cosmo_band_partial"

    if accepted:
        epsilon_min = accepted_eps[0]
        epsilon_max = accepted_eps[-1]
    else:
        epsilon_min = None
        epsilon_max = None

    return {
        "accepted": accepted,
        "accepted_count": len(accepted),
        "accepted_components_epsilon": connected_components_1d(accepted_eps),
        "accepted_components_pi": connected_components_1d(accepted_pi),
        "epsilon_min_acceptable": epsilon_min,
        "epsilon_max_acceptable": epsilon_max,
        "best_fit_epsilon": best["epsilon"],
        "best_fit_pi_cosmo": best["pi_cosmo"],
        "best_fit_G_eff_cosmo": best["G_eff_cosmo"],
        "best_fit_F_temps_cosmo": best["F_temps_cosmo"],
        "best_fit_chi_total": best["chi_total"],
        "best_fit_chi_sn": best["chi_sn"],
        "best_fit_chi_bao": best["chi_bao"],
        "best_fit_chi_cmb": best["chi_cmb"],
        "best_fit_chi_growth": best["chi_growth"],
        "best_fit_DA_rec": best["DA_rec"],
        "best_fit_first_peak_shift": best["first_peak_shift"],
        "verdict": verdict,
        "notes": [
            "V84 is a toy cosmology confrontation, not a full Boltzmann-code replacement.",
            "The pi_n^{cosmo} cases are intended to separate a nearly standard regime from a mild deformation regime.",
        ],
    }


def write_csv(rows: list[dict[str, float]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "epsilon",
        "delta_em",
        "pi_cosmo",
        "G_eff_cosmo",
        "F_temps_cosmo",
        "omega_m_eff",
        "H_ratio_z0",
        "H_ratio_z05",
        "H_ratio_z1",
        "H_ratio_z2",
        "DA_rec",
        "DL_z0_5",
        "DL_z1",
        "f_sigma8_proxy_z0",
        "f_sigma8_proxy_z05",
        "f_sigma8_proxy_z1",
        "first_peak_shift",
        "chi_sn",
        "chi_bao",
        "chi_cmb",
        "chi_growth",
        "chi_total",
        "passes_bbn",
        "passes_cosmo",
        "passes_all",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v84_cosmo_extension_summary_{timestamp}.json"
    txt_path = output_dir / f"v84_cosmo_extension_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V84 cosmology extension summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"accepted_count: {summary['accepted_count']}/{summary['total']}",
        f"epsilon_min_acceptable: {summary['epsilon_min_acceptable']}",
        f"epsilon_max_acceptable: {summary['epsilon_max_acceptable']}",
        f"best_fit_epsilon: {summary['best_fit_epsilon']}",
        f"best_fit_pi_cosmo: {summary['best_fit_pi_cosmo']}",
        f"best_fit_G_eff_cosmo: {summary['best_fit_G_eff_cosmo']}",
        f"best_fit_F_temps_cosmo: {summary['best_fit_F_temps_cosmo']}",
        f"best_fit_chi_total: {summary['best_fit_chi_total']}",
        f"best_fit_chi_sn: {summary['best_fit_chi_sn']}",
        f"best_fit_chi_bao: {summary['best_fit_chi_bao']}",
        f"best_fit_chi_cmb: {summary['best_fit_chi_cmb']}",
        f"best_fit_chi_growth: {summary['best_fit_chi_growth']}",
        f"best_fit_DA_rec: {summary['best_fit_DA_rec']}",
        f"best_fit_first_peak_shift: {summary['best_fit_first_peak_shift']}",
        "",
        "Notes:",
    ]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_v84_cosmo_extension(
    output_dir: str | Path | None = None,
    epsilon_min: float = -0.0076,
    epsilon_max: float = -0.0063,
    epsilon_points: int = 14,
    pi_cosmo_values: list[float] | None = None,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v84_cosmo_extension"

    if pi_cosmo_values is None:
        pi_cosmo_values = [0.0, 0.01, 0.03, 0.1]

    epsilon_values = [round(value, 4) for value in linspace(epsilon_min, epsilon_max, epsilon_points)]
    rows = scan_epsilon(
        epsilon_values,
        pi_cosmo_values,
        rho_lab=1.0e-16,
        rho_cosmo=1.0,
        h0=67.4,
        omega_m=0.315,
        omega_l=0.685,
        omega_r=9.0e-5,
    )

    summary = summarize(rows)
    summary.update(
        {
            "suite": "v84_cosmo_extension",
            "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
            "epsilon_range": [epsilon_min, epsilon_max, epsilon_points],
            "pi_cosmo_values": pi_cosmo_values,
            "total": len(rows),
            "rows": rows,
        }
    )
    csv_path = result_dir / "v84_cosmo_extension_results.csv"
    write_csv(rows, csv_path)
    json_path, txt_path = write_summary(summary, result_dir)
    summary.update(
        {
            "csv_path": str(csv_path),
            "json_path": str(json_path),
            "txt_path": str(txt_path),
        }
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V84 toy cosmology extension.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    parser.add_argument("--epsilon-min", type=float, default=-0.0076, help="Minimum epsilon value to scan")
    parser.add_argument("--epsilon-max", type=float, default=-0.0063, help="Maximum epsilon value to scan")
    parser.add_argument("--epsilon-points", type=int, default=14, help="Number of epsilon grid points")
    args = parser.parse_args()

    result = run_v84_cosmo_extension(
        output_dir=args.output_dir,
        epsilon_min=args.epsilon_min,
        epsilon_max=args.epsilon_max,
        epsilon_points=args.epsilon_points,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()