"""Run the V83 coupling calibration at fixed epsilon and summarize the results."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def delta_em_from_epsilon(epsilon: float, k_em: float = 1.0) -> float:
    return k_em * epsilon


def pi_n(epsilon: float, density_ratio: float, k_n: float) -> float:
    return max(0.0, -k_n * epsilon * density_ratio)


def g_eff(epsilon: float, pi_n_value: float, k_g: float) -> float:
    return 1.0 + k_g * abs(epsilon) * pi_n_value


def f_temps(epsilon: float, pi_n_value: float, k_t: float) -> float:
    return 1.0 / (1.0 + k_t * abs(epsilon) * pi_n_value)


def calibrate_k_n(epsilon: float) -> float:
    return 1.0 / abs(epsilon)


def calibrate_k_t(epsilon: float, target_z: float = 0.30) -> float:
    return target_z / abs(epsilon)


def calibrate_k_g(epsilon: float, target_g_eff_ns: float = 1.28) -> float:
    return (target_g_eff_ns - 1.0) / abs(epsilon)


def ns_mass_max(g_eff_ns: float, f_temps_ns: float) -> float:
    return 2.0 + 0.15 * (g_eff_ns - 1.0) - 0.04 * (1.0 - f_temps_ns)


def ns_radius_14(g_eff_ns: float, f_temps_ns: float) -> float:
    return 12.5 - 3.8 * (g_eff_ns - 1.0) - 1.6 * (1.0 - f_temps_ns)


def ns_redshift_effective(f_temps_ns: float) -> float:
    return 1.0 / f_temps_ns - 1.0


def summarize(epsilon: float) -> dict[str, object]:
    k_n = calibrate_k_n(epsilon)
    k_t = calibrate_k_t(epsilon)
    k_g = calibrate_k_g(epsilon)

    delta_em = delta_em_from_epsilon(epsilon)
    pi_lab = pi_n(epsilon, 1.0e-16, k_n)
    pi_ns = pi_n(epsilon, 1.0, k_n)
    g_lab = g_eff(epsilon, pi_lab, k_g)
    g_ns = g_eff(epsilon, pi_ns, k_g)
    t_lab = f_temps(epsilon, pi_lab, k_t)
    t_ns = f_temps(epsilon, pi_ns, k_t)
    z_eff = ns_redshift_effective(t_ns)
    m_max = ns_mass_max(g_ns, t_ns)
    r14 = ns_radius_14(g_ns, t_ns)
    variation_em_lab = abs(delta_em) * pi_lab

    verdict = (
        "v83_calibration_confirmed"
        if (
            -0.008 <= delta_em <= -0.0059
            and variation_em_lab < 1.0e-16
            and abs(pi_ns - 1.0) <= 0.05
            and abs(g_lab - 1.0) <= 2.0e-5
            and 0.2 <= z_eff <= 0.4
            and 2.01 <= m_max <= 2.08
            and 11.0 <= r14 <= 14.0
        )
        else "v83_calibration_tension"
    )

    return {
        "suite": "v83_coupling_calibration",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "epsilon_best": epsilon,
        "delta_em": delta_em,
        "k_n_calibrated": k_n,
        "k_t_calibrated": k_t,
        "k_g_calibrated": k_g,
        "pi_n_labo": pi_lab,
        "pi_n_ns": pi_ns,
        "G_eff_labo": g_lab,
        "G_eff_ns": g_ns,
        "F_temps_labo": t_lab,
        "F_temps_ns": t_ns,
        "z_eff": z_eff,
        "M_max": m_max,
        "R_1p4": r14,
        "variation_em_labo": variation_em_lab,
        "notes": [
            "V83 fixe epsilon et calibre les couplages pour les fenêtres gravité/temps/NS.",
            "Les proxys restent phénoménologiques mais gardent les bons ordres de grandeur d'observation.",
        ],
    }


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v83_coupling_calibration_summary_{timestamp}.json"
    txt_path = output_dir / f"v83_coupling_calibration_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V83 coupling calibration summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"epsilon_best: {summary['epsilon_best']}",
        f"delta_em: {summary['delta_em']}",
        f"k_n_calibrated: {summary['k_n_calibrated']}",
        f"k_t_calibrated: {summary['k_t_calibrated']}",
        f"k_g_calibrated: {summary['k_g_calibrated']}",
        f"pi_n_labo: {summary['pi_n_labo']}",
        f"pi_n_ns: {summary['pi_n_ns']}",
        f"G_eff_labo: {summary['G_eff_labo']}",
        f"G_eff_ns: {summary['G_eff_ns']}",
        f"F_temps_labo: {summary['F_temps_labo']}",
        f"F_temps_ns: {summary['F_temps_ns']}",
        f"z_eff: {summary['z_eff']}",
        f"M_max: {summary['M_max']}",
        f"R_1p4: {summary['R_1p4']}",
        f"variation_em_labo: {summary['variation_em_labo']}",
        "",
        "Notes:",
    ]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_calibration(epsilon: float = -0.0069, output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v83_coupling_calibration"
    summary = summarize(epsilon)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V83 coupling calibration and summarize the results.")
    parser.add_argument("--epsilon", type=float, default=-0.0069, help="Fixed epsilon from V82")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_calibration(args.epsilon, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()