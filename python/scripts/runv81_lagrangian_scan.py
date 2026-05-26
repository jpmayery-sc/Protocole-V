"""Run the V81 minimal-Lagrangian scan and summarize the epsilon band."""
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


def scan_epsilon(
    epsilon_min: float,
    epsilon_max: float,
    step: float,
    *,
    k_em: float,
    k_n: float,
    k_g: float,
    k_t: float,
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
        rows.append(
            {
                "epsilon": epsilon,
                "delta_em": delta_em,
                "pi_n_lab": pi_lab,
                "pi_n_ns": pi_ns,
                "G_eff_lab": g_lab,
                "G_eff_ns": g_ns,
                "F_temps_lab": t_lab,
                "F_temps_ns": t_ns,
                "passes_delta": -0.008 <= delta_em <= -0.0059,
                "passes_lab": pi_lab <= 1.0e-3 and math.isclose(g_lab, 1.0, rel_tol=1.0e-3, abs_tol=1.0e-3),
                "passes_ns": 0.9 <= pi_ns <= 1.1 and g_ns > 1.0 and t_ns < 1.0,
            }
        )
        rows[-1]["passes_all"] = rows[-1]["passes_delta"] and rows[-1]["passes_lab"] and rows[-1]["passes_ns"]
        epsilon = round(epsilon + step, 12)
    return rows


def summarize(rows: list[dict[str, float]], *, k_em: float, k_n: float, k_g: float, k_t: float) -> dict[str, object]:
    accepted_rows = [row for row in rows if row["passes_all"]]
    if accepted_rows:
        epsilon_min = min(row["epsilon"] for row in accepted_rows)
        epsilon_max = max(row["epsilon"] for row in accepted_rows)
        epsilon_center = (epsilon_min + epsilon_max) / 2.0
        best_row = min(
            accepted_rows,
            key=lambda row: abs(row["delta_em"] + 0.0068) + abs(row["pi_n_ns"] - 1.0) + abs(row["G_eff_ns"] - 1.0),
        )
        verdict = "lagrangian_band_confirmed"
    else:
        epsilon_min = None
        epsilon_max = None
        epsilon_center = None
        best_row = min(rows, key=lambda row: abs(row["delta_em"] + 0.0068) + abs(row["pi_n_ns"] - 1.0) + abs(row["G_eff_ns"] - 1.0))
        verdict = "no_full_band"

    return {
        "suite": "v81_lagrangian_scan",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "v81_global_verdict": verdict,
        "accepted_count": len(accepted_rows),
        "total": len(rows),
        "epsilon_min_acceptable": epsilon_min,
        "epsilon_max_acceptable": epsilon_max,
        "epsilon_central_value": epsilon_center,
        "best_fit_epsilon": best_row["epsilon"],
        "best_fit_delta_em": best_row["delta_em"],
        "best_fit_pi_n_ns": best_row["pi_n_ns"],
        "best_fit_G_eff_ns": best_row["G_eff_ns"],
        "best_fit_F_temps_ns": best_row["F_temps_ns"],
        "rows": accepted_rows,
        "k_em": k_em,
        "k_n": k_n,
        "k_g": k_g,
        "k_t": k_t,
        "notes": [
            "V81 = Lagrangien minimal, calibré sur la fenêtre BBN de V80.",
            "Le scan reste phénoménologique et ne prétend pas dériver un champ complet de première principe.",
        ],
    }


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v81_lagrangian_scan_summary_{timestamp}.json"
    txt_path = output_dir / f"v81_lagrangian_scan_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V81 minimal-Lagrangian scan summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"accepted_count: {summary['accepted_count']}/{summary['total']}",
        f"epsilon_min_acceptable: {summary['epsilon_min_acceptable']}",
        f"epsilon_max_acceptable: {summary['epsilon_max_acceptable']}",
        f"epsilon_central_value: {summary['epsilon_central_value']}",
        f"best_fit_epsilon: {summary['best_fit_epsilon']}",
        f"best_fit_delta_em: {summary['best_fit_delta_em']}",
        f"best_fit_pi_n_ns: {summary['best_fit_pi_n_ns']}",
        f"best_fit_G_eff_ns: {summary['best_fit_G_eff_ns']}",
        f"best_fit_F_temps_ns: {summary['best_fit_F_temps_ns']}",
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
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v81_lagrangian"

    # Calibration chosen to map V80's delta_EM band to epsilon directly.
    k_em = 1.0
    k_n = 1.0 / 0.00695
    k_g = 8.0
    k_t = 6.0

    rows = scan_epsilon(epsilon_min, epsilon_max, step, k_em=k_em, k_n=k_n, k_g=k_g, k_t=k_t)
    summary = summarize(rows, k_em=k_em, k_n=k_n, k_g=k_g, k_t=k_t)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V81 minimal-Lagrangian scan and summarize the epsilon band.")
    parser.add_argument("--epsilon-min", type=float, default=-0.008, help="Minimum epsilon value to scan")
    parser.add_argument("--epsilon-max", type=float, default=-0.0059, help="Maximum epsilon value to scan")
    parser.add_argument("--step", type=float, default=0.0001, help="Scan step for epsilon")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_scan(args.epsilon_min, args.epsilon_max, args.step, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()