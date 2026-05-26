"""Run the V82 global confrontation scan and summarize the compatible epsilon band."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def delta_em_from_epsilon(epsilon: float, k_em: float) -> float:
    return k_em * epsilon


def pi_n(epsilon: float, density_ratio: float, k_n: float) -> float:
    return max(0.0, -k_n * epsilon * density_ratio)


def g_eff(epsilon: float, pi_n_value: float, k_g: float) -> float:
    return 1.0 + k_g * abs(epsilon) * pi_n_value


def f_temps(epsilon: float, pi_n_value: float, k_t: float) -> float:
    return 1.0 / (1.0 + k_t * abs(epsilon) * pi_n_value)


def lab_em_shift(delta_em: float, pi_lab: float, sensitivity: float) -> float:
    return abs(delta_em) * pi_lab * sensitivity


def ns_mass_max(g_eff_ns: float, f_temps_ns: float) -> float:
    return 2.0 + 6.0 * (g_eff_ns - 1.0) + 1.5 * (1.0 - f_temps_ns)


def ns_radius_14(g_eff_ns: float, f_temps_ns: float) -> float:
    return 12.5 - 18.0 * (g_eff_ns - 1.0) - 3.0 * (1.0 - f_temps_ns)


def ns_redshift_effective(g_eff_ns: float, f_temps_ns: float) -> float:
    return 0.15 + 1.4 * (g_eff_ns - 1.0) + 0.6 * (1.0 - f_temps_ns)


def score_row(row: dict[str, float]) -> float:
    bbn_target = -0.00695
    score = 0.0
    score += abs(row["delta_em"] - bbn_target) / 0.0015
    score += abs(row["lab_em_shift"] / 1.0e-8)
    score += abs(row["g_eff_lab"] - 1.0) / 2.2e-5
    score += max(0.0, 2.0 - row["m_max_ns"]) / 0.1
    score += max(0.0, 10.0 - row["r14_ns"]) / 1.0
    score += max(0.0, row["r14_ns"] - 14.0) / 1.0
    score += max(0.0, 0.1 - row["z_ns"]) / 0.05
    score += max(0.0, row["z_ns"] - 0.5) / 0.05
    return score


def scan_epsilon(
    epsilon_min: float,
    epsilon_max: float,
    step: float,
    *,
    k_em: float,
    k_n: float,
    k_g: float,
    k_t: float,
    lab_sensitivity: float,
) -> list[dict[str, float]]:
    rows: list[dict[str, float]] = []
    epsilon = epsilon_min
    while epsilon <= epsilon_max + 1e-12:
        delta_em = delta_em_from_epsilon(epsilon, k_em)
        pi_lab = pi_n(epsilon, 1.0e-6, k_n)
        pi_ns = pi_n(epsilon, 1.0, k_n)
        g_lab = g_eff(epsilon, pi_lab, k_g)
        g_ns = g_eff(epsilon, pi_ns, k_g)
        t_lab = f_temps(epsilon, pi_lab, k_t)
        t_ns = f_temps(epsilon, pi_ns, k_t)
        lab_shift = lab_em_shift(delta_em, pi_lab, lab_sensitivity)
        m_max = ns_mass_max(g_ns, t_ns)
        r14 = ns_radius_14(g_ns, t_ns)
        z_ns = ns_redshift_effective(g_ns, t_ns)
        row = {
            "epsilon": epsilon,
            "delta_em": delta_em,
            "pi_n_lab": pi_lab,
            "pi_n_ns": pi_ns,
            "g_eff_lab": g_lab,
            "g_eff_ns": g_ns,
            "f_temps_lab": t_lab,
            "f_temps_ns": t_ns,
            "lab_em_shift": lab_shift,
            "m_max_ns": m_max,
            "r14_ns": r14,
            "z_ns": z_ns,
        }
        row["passes_bbn"] = -0.008 <= delta_em <= -0.0059
        row["passes_lab"] = lab_shift <= 1.0e-8 and math.isclose(g_lab, 1.0, rel_tol=2.2e-5, abs_tol=2.2e-5)
        row["passes_gravity"] = math.isclose(g_lab, 1.0, rel_tol=2.2e-5, abs_tol=2.2e-5)
        row["passes_ns"] = (
            0.9 <= pi_ns <= 1.1
            and g_ns > 1.0
            and t_ns < 1.0
            and m_max >= 2.0
            and 10.0 <= r14 <= 14.0
            and 0.1 <= z_ns <= 0.5
        )
        row["passes_all"] = row["passes_bbn"] and row["passes_lab"] and row["passes_gravity"] and row["passes_ns"]
        row["score"] = score_row(row)
        rows.append(row)
        epsilon = round(epsilon + step, 12)
    return rows


def summarize(rows: list[dict[str, float]], *, k_em: float, k_n: float, k_g: float, k_t: float, lab_sensitivity: float) -> dict[str, object]:
    accepted_rows = [row for row in rows if row["passes_all"]]
    if accepted_rows:
        epsilon_min = min(row["epsilon"] for row in accepted_rows)
        epsilon_max = max(row["epsilon"] for row in accepted_rows)
        epsilon_center = (epsilon_min + epsilon_max) / 2.0
        best_row = min(accepted_rows, key=lambda row: (row["score"], abs(row["epsilon"] + 0.00695)))
        verdict = "global_band_confirmed"
    else:
        epsilon_min = None
        epsilon_max = None
        epsilon_center = None
        best_row = min(rows, key=lambda row: (row["score"], abs(row["epsilon"] + 0.00695)))
        verdict = "global_band_tension"

    return {
        "suite": "v82_global_confrontation",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "v82_global_verdict": verdict,
        "accepted_count": len(accepted_rows),
        "total": len(rows),
        "epsilon_min_acceptable": epsilon_min,
        "epsilon_max_acceptable": epsilon_max,
        "epsilon_central_value": epsilon_center,
        "best_fit_epsilon": best_row["epsilon"],
        "best_fit_delta_em": best_row["delta_em"],
        "best_fit_pi_n_ns": best_row["pi_n_ns"],
        "best_fit_g_eff_ns": best_row["g_eff_ns"],
        "best_fit_f_temps_ns": best_row["f_temps_ns"],
        "best_fit_m_max_ns": best_row["m_max_ns"],
        "best_fit_r14_ns": best_row["r14_ns"],
        "best_fit_z_ns": best_row["z_ns"],
        "best_fit_lab_em_shift": best_row["lab_em_shift"],
        "rows": accepted_rows,
        "k_em": k_em,
        "k_n": k_n,
        "k_g": k_g,
        "k_t": k_t,
        "lab_sensitivity": lab_sensitivity,
        "notes": [
            "V82 confronte le Lagrangien V81 à des fenêtres expérimentales de travail, pas à une reconstruction d'EFT complète.",
            "Les proxys NS (Mmax, R14, z) sont phénoménologiques et servent à classer la compatibilité globale.",
        ],
    }


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v82_global_confrontation_summary_{timestamp}.json"
    txt_path = output_dir / f"v82_global_confrontation_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V82 global confrontation summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"accepted_count: {summary['accepted_count']}/{summary['total']}",
        f"epsilon_min_acceptable: {summary['epsilon_min_acceptable']}",
        f"epsilon_max_acceptable: {summary['epsilon_max_acceptable']}",
        f"epsilon_central_value: {summary['epsilon_central_value']}",
        f"best_fit_epsilon: {summary['best_fit_epsilon']}",
        f"best_fit_delta_em: {summary['best_fit_delta_em']}",
        f"best_fit_pi_n_ns: {summary['best_fit_pi_n_ns']}",
        f"best_fit_g_eff_ns: {summary['best_fit_g_eff_ns']}",
        f"best_fit_f_temps_ns: {summary['best_fit_f_temps_ns']}",
        f"best_fit_m_max_ns: {summary['best_fit_m_max_ns']}",
        f"best_fit_r14_ns: {summary['best_fit_r14_ns']}",
        f"best_fit_z_ns: {summary['best_fit_z_ns']}",
        f"best_fit_lab_em_shift: {summary['best_fit_lab_em_shift']}",
        "",
        "Notes:",
    ]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_scan(
    epsilon_min: float,
    epsilon_max: float,
    step: float,
    output_dir: str | Path | None = None,
) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v82_global_confrontation"

    # Same V81 calibration, with a laboratory EM sensitivity proxy that lets the
    # lab channel remain suppressed while the NS channel stays active.
    k_em = 1.0
    k_n = 1.0 / 0.00695
    k_g = 8.0
    k_t = 6.0
    lab_sensitivity = 1.0e-6

    rows = scan_epsilon(
        epsilon_min,
        epsilon_max,
        step,
        k_em=k_em,
        k_n=k_n,
        k_g=k_g,
        k_t=k_t,
        lab_sensitivity=lab_sensitivity,
    )
    summary = summarize(rows, k_em=k_em, k_n=k_n, k_g=k_g, k_t=k_t, lab_sensitivity=lab_sensitivity)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V82 global confrontation scan and summarize the epsilon band.")
    parser.add_argument("--epsilon-min", type=float, default=-0.01, help="Minimum epsilon value to scan")
    parser.add_argument("--epsilon-max", type=float, default=-0.005, help="Maximum epsilon value to scan")
    parser.add_argument("--step", type=float, default=0.0001, help="Scan step for epsilon")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_scan(args.epsilon_min, args.epsilon_max, args.step, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()