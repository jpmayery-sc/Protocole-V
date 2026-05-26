"""Check a single instrumentation on s/p/d/f families.

The goal is to compare one global baseline model against one global corrected
model on the four block families at once:

    radius ~ 1 + Z_eff
    radius ~ 1 + Z_eff + l_valence + l_core

The script reports the global fit quality and the per-family residual quality
for alkali (s), halogen (p), transition d blocks, and lanthanides (f).
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6

GROUPS = {
    "s": {
        "l_valence": 0.0,
        "l_core": 0.0,
        "items": [
            {"symbol": "Li", "period": 2, "radius_pm": 152.0, "ionization_ev": 5.3917},
            {"symbol": "Na", "period": 3, "radius_pm": 186.0, "ionization_ev": 5.1391},
            {"symbol": "K", "period": 4, "radius_pm": 227.0, "ionization_ev": 4.3407},
            {"symbol": "Rb", "period": 5, "radius_pm": 248.0, "ionization_ev": 4.1771},
            {"symbol": "Cs", "period": 6, "radius_pm": 267.0, "ionization_ev": 3.8939},
        ],
    },
    "p": {
        "l_valence": 1.0,
        "l_core": 0.0,
        "items": [
            {"symbol": "F", "period": 2, "radius_pm": 50.0, "ionization_ev": 17.4228},
            {"symbol": "Cl", "period": 3, "radius_pm": 79.0, "ionization_ev": 12.9676},
            {"symbol": "Br", "period": 4, "radius_pm": 94.0, "ionization_ev": 11.8138},
            {"symbol": "I", "period": 5, "radius_pm": 115.0, "ionization_ev": 10.4513},
        ],
    },
    "d": {
        "l_valence": 2.0,
        "l_core": 1.0,
        "items": [
            {"symbol": "Sc", "period": 4, "radius_pm": 162.0, "ionization_ev": 6.5615},
            {"symbol": "Ti", "period": 4, "radius_pm": 147.0, "ionization_ev": 6.8281},
            {"symbol": "V", "period": 4, "radius_pm": 134.0, "ionization_ev": 6.7462},
            {"symbol": "Cr", "period": 4, "radius_pm": 128.0, "ionization_ev": 6.7665},
            {"symbol": "Mn", "period": 4, "radius_pm": 127.0, "ionization_ev": 7.4340},
            {"symbol": "Fe", "period": 4, "radius_pm": 126.0, "ionization_ev": 7.9024},
            {"symbol": "Co", "period": 4, "radius_pm": 125.0, "ionization_ev": 7.8810},
            {"symbol": "Ni", "period": 4, "radius_pm": 124.0, "ionization_ev": 7.6398},
            {"symbol": "Cu", "period": 4, "radius_pm": 128.0, "ionization_ev": 7.7264},
            {"symbol": "Zn", "period": 4, "radius_pm": 134.0, "ionization_ev": 9.3942},
            {"symbol": "Y", "period": 5, "radius_pm": 180.0, "ionization_ev": 6.2173},
            {"symbol": "Zr", "period": 5, "radius_pm": 155.0, "ionization_ev": 6.6339},
            {"symbol": "Nb", "period": 5, "radius_pm": 146.0, "ionization_ev": 6.7589},
            {"symbol": "Mo", "period": 5, "radius_pm": 139.0, "ionization_ev": 7.0924},
            {"symbol": "Tc", "period": 5, "radius_pm": 136.0, "ionization_ev": 7.2800},
            {"symbol": "Ru", "period": 5, "radius_pm": 134.0, "ionization_ev": 7.3605},
            {"symbol": "Rh", "period": 5, "radius_pm": 134.0, "ionization_ev": 7.4589},
            {"symbol": "Pd", "period": 5, "radius_pm": 137.0, "ionization_ev": 8.3369},
            {"symbol": "Ag", "period": 5, "radius_pm": 144.0, "ionization_ev": 7.5762},
            {"symbol": "Cd", "period": 5, "radius_pm": 151.0, "ionization_ev": 8.9938},
            {"symbol": "Hf", "period": 6, "radius_pm": 159.0, "ionization_ev": 6.8251},
            {"symbol": "Ta", "period": 6, "radius_pm": 146.0, "ionization_ev": 7.5496},
            {"symbol": "W", "period": 6, "radius_pm": 139.0, "ionization_ev": 7.8640},
            {"symbol": "Re", "period": 6, "radius_pm": 137.0, "ionization_ev": 7.8335},
            {"symbol": "Os", "period": 6, "radius_pm": 135.0, "ionization_ev": 8.4382},
            {"symbol": "Ir", "period": 6, "radius_pm": 136.0, "ionization_ev": 8.9670},
            {"symbol": "Pt", "period": 6, "radius_pm": 139.0, "ionization_ev": 8.9588},
            {"symbol": "Au", "period": 6, "radius_pm": 144.0, "ionization_ev": 9.2255},
            {"symbol": "Hg", "period": 6, "radius_pm": 151.0, "ionization_ev": 10.4375},
        ],
    },
    "f": {
        "l_valence": 3.0,
        "l_core": 2.0,
        "items": [
            {"symbol": "La", "period": 6, "radius_pm": 195.0, "ionization_ev": 5.5770},
            {"symbol": "Ce", "period": 6, "radius_pm": 185.0, "ionization_ev": 5.5387},
            {"symbol": "Pr", "period": 6, "radius_pm": 182.0, "ionization_ev": 5.4730},
            {"symbol": "Nd", "period": 6, "radius_pm": 181.0, "ionization_ev": 5.5250},
            {"symbol": "Sm", "period": 6, "radius_pm": 180.0, "ionization_ev": 5.6440},
            {"symbol": "Eu", "period": 6, "radius_pm": 199.0, "ionization_ev": 5.6700},
            {"symbol": "Gd", "period": 6, "radius_pm": 180.0, "ionization_ev": 6.1500},
            {"symbol": "Tb", "period": 6, "radius_pm": 178.0, "ionization_ev": 5.8630},
            {"symbol": "Dy", "period": 6, "radius_pm": 177.0, "ionization_ev": 5.9390},
            {"symbol": "Ho", "period": 6, "radius_pm": 176.0, "ionization_ev": 6.0220},
            {"symbol": "Er", "period": 6, "radius_pm": 175.0, "ionization_ev": 6.1080},
            {"symbol": "Tm", "period": 6, "radius_pm": 174.0, "ionization_ev": 6.1840},
            {"symbol": "Yb", "period": 6, "radius_pm": 194.0, "ionization_ev": 6.2540},
            {"symbol": "Lu", "period": 6, "radius_pm": 173.0, "ionization_ev": 5.4280},
        ],
    },
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def solve_linear_system(matrix: list[list[float]], vector: list[float]) -> list[float]:
    size = len(vector)
    augmented = [row[:] + [value] for row, value in zip(matrix, vector)]

    for pivot_index in range(size):
        pivot_row = max(range(pivot_index, size), key=lambda row_index: abs(augmented[row_index][pivot_index]))
        if abs(augmented[pivot_row][pivot_index]) < 1e-12:
            raise ValueError("singular system")
        if pivot_row != pivot_index:
            augmented[pivot_index], augmented[pivot_row] = augmented[pivot_row], augmented[pivot_index]

        pivot = augmented[pivot_index][pivot_index]
        for column_index in range(pivot_index, size + 1):
            augmented[pivot_index][column_index] /= pivot

        for row_index in range(size):
            if row_index == pivot_index:
                continue
            factor = augmented[row_index][pivot_index]
            for column_index in range(pivot_index, size + 1):
                augmented[row_index][column_index] -= factor * augmented[pivot_index][column_index]

    return [augmented[row_index][size] for row_index in range(size)]


def fit_multivariate(rows: list[list[float]], targets: list[float]) -> dict:
    columns = len(rows[0])
    xtx = [[0.0 for _ in range(columns)] for _ in range(columns)]
    xty = [0.0 for _ in range(columns)]

    for row, target in zip(rows, targets):
        for i in range(columns):
            xty[i] += row[i] * target
            for j in range(columns):
                xtx[i][j] += row[i] * row[j]

    coefficients = solve_linear_system(xtx, xty)
    predicted = [sum(coefficient * value for coefficient, value in zip(coefficients, row)) for row in rows]
    residuals = [target - prediction for target, prediction in zip(targets, predicted)]
    rmse = math.sqrt(sum(residual * residual for residual in residuals) / len(residuals))
    return {
        "coefficients": coefficients,
        "predicted": predicted,
        "residuals": residuals,
        "rmse": rmse,
        "max_abs_residual": max(abs(residual) for residual in residuals),
    }


def build_rows() -> dict:
    items = []
    for group_name, group in GROUPS.items():
        for item in group["items"]:
            zeff = estimate_zeff(item["ionization_ev"], int(item["period"]))
            items.append(
                {
                    **item,
                    "group": group_name,
                    "l_valence": float(group["l_valence"]),
                    "l_core": float(group["l_core"]),
                    "zeff_proxy": round(zeff, 6),
                }
            )
    return {"series": items}


def family_stats(series: list[dict], predicted: list[float], corrected_predicted: list[float]) -> dict:
    baseline_residuals = [item["radius_pm"] - pred for item, pred in zip(series, predicted)]
    corrected_residuals = [item["radius_pm"] - pred for item, pred in zip(series, corrected_predicted)]
    groups = sorted({item["group"] for item in series})
    group_results = {}
    improved_groups = 0

    for group in groups:
        indices = [index for index, item in enumerate(series) if item["group"] == group]
        baseline_group = [baseline_residuals[index] for index in indices]
        corrected_group = [corrected_residuals[index] for index in indices]
        baseline_rmse = math.sqrt(sum(value * value for value in baseline_group) / len(baseline_group))
        corrected_rmse = math.sqrt(sum(value * value for value in corrected_group) / len(corrected_group))
        improved = corrected_rmse < baseline_rmse
        improved_groups += int(improved)
        group_results[group] = {
            "baseline_rmse": baseline_rmse,
            "corrected_rmse": corrected_rmse,
            "improved": improved,
        }

    return {
        "group_results": group_results,
        "improved_groups": improved_groups,
        "group_count": len(groups),
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    observables = build_rows()
    series = observables["series"]

    baseline_rows = [[1.0, item["zeff_proxy"]] for item in series]
    corrected_rows = [[1.0, item["zeff_proxy"], item["l_valence"], item["l_core"]] for item in series]
    radii = [item["radius_pm"] for item in series]

    baseline = fit_multivariate(baseline_rows, radii)
    corrected = fit_multivariate(corrected_rows, radii)

    stats = family_stats(series, baseline["predicted"], corrected["predicted"])
    corrected_better = corrected["rmse"] < baseline["rmse"] and corrected["max_abs_residual"] <= baseline["max_abs_residual"]
    enough_groups = stats["improved_groups"] >= 3
    verdict = "supported" if corrected_better and enough_groups else ("partiel" if corrected_better else "contradicted")

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "corrected_better": corrected_better,
        "baseline": baseline,
        "corrected": corrected,
        "group_summary": stats,
        "hypothesis": "one shared instrumentation can compare s, p, d and f families through the same core/valence correction",
        "case_control": "one global baseline radius fit against Z_eff versus one global corrected fit against [1, Z_eff, l_valence, l_core]",
        "observable": "global residuals and per-family residuals across s/p/d/f blocks",
        "series": series,
        "falsifiers": [
            "the corrected model is not globally better than the baseline",
            "fewer than three of the four block families improve",
            "one block family blows up the residuals instead of shrinking them",
        ],
    }

    json_path = outdir / f"spd_f_instrumentation_check_{timestamp}.json"
    txt_path = outdir / f"spd_f_instrumentation_check_{timestamp}.txt"
    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "s/p/d/f unified instrumentation check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"corrected_better: {corrected_better}",
        f"improved_groups: {stats['improved_groups']}/{stats['group_count']}",
        "",
        "Global fits:",
        f"- baseline rmse: {baseline['rmse']:.6f}",
        f"- corrected rmse: {corrected['rmse']:.6f}",
        f"- baseline max_abs_residual: {baseline['max_abs_residual']:.6f}",
        f"- corrected max_abs_residual: {corrected['max_abs_residual']:.6f}",
        "",
        "Per-family summary:",
    ]
    for group_name, result in stats["group_results"].items():
        lines.append(
            f"- {group_name}: baseline_rmse={result['baseline_rmse']:.6f} corrected_rmse={result['corrected_rmse']:.6f} improved={result['improved']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Check a single instrumentation across s/p/d/f families.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()