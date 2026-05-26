"""Check whether Zeff-vs-Z slopes scale like A(l + 1/2) across s/p/d/f families."""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


R_H_EV = 13.6
SLOPE_TOLERANCE = 0.25

SERIES = {
    "s_alkali": {
        "l": 0,
        "cases": [
            {"symbol": "Li", "Z": 3, "n": 2, "ionization_ev": 5.3917},
            {"symbol": "Na", "Z": 11, "n": 3, "ionization_ev": 5.1391},
            {"symbol": "K", "Z": 19, "n": 4, "ionization_ev": 4.3407},
            {"symbol": "Rb", "Z": 37, "n": 5, "ionization_ev": 4.1771},
            {"symbol": "Cs", "Z": 55, "n": 6, "ionization_ev": 3.8939},
        ],
    },
    "p_halogen": {
        "l": 1,
        "cases": [
            {"symbol": "F", "Z": 9, "n": 2, "ionization_ev": 17.4228},
            {"symbol": "Cl", "Z": 17, "n": 3, "ionization_ev": 12.9676},
            {"symbol": "Br", "Z": 35, "n": 4, "ionization_ev": 11.8138},
            {"symbol": "I", "Z": 53, "n": 5, "ionization_ev": 10.4513},
        ],
    },
    "d_3d": {
        "l": 2,
        "cases": [
            {"symbol": "Sc", "Z": 21, "n": 4, "ionization_ev": 6.5615},
            {"symbol": "Ti", "Z": 22, "n": 4, "ionization_ev": 6.8281},
            {"symbol": "V", "Z": 23, "n": 4, "ionization_ev": 6.7462},
            {"symbol": "Cr", "Z": 24, "n": 4, "ionization_ev": 6.7665},
            {"symbol": "Mn", "Z": 25, "n": 4, "ionization_ev": 7.4340},
            {"symbol": "Fe", "Z": 26, "n": 4, "ionization_ev": 7.9024},
            {"symbol": "Co", "Z": 27, "n": 4, "ionization_ev": 7.8810},
            {"symbol": "Ni", "Z": 28, "n": 4, "ionization_ev": 7.6398},
            {"symbol": "Cu", "Z": 29, "n": 4, "ionization_ev": 7.7264},
            {"symbol": "Zn", "Z": 30, "n": 4, "ionization_ev": 9.3942},
        ],
    },
    "d_4d": {
        "l": 2,
        "cases": [
            {"symbol": "Y", "Z": 39, "n": 5, "ionization_ev": 6.2173},
            {"symbol": "Zr", "Z": 40, "n": 5, "ionization_ev": 6.6339},
            {"symbol": "Nb", "Z": 41, "n": 5, "ionization_ev": 6.7589},
            {"symbol": "Mo", "Z": 42, "n": 5, "ionization_ev": 7.0924},
            {"symbol": "Tc", "Z": 43, "n": 5, "ionization_ev": 7.2800},
            {"symbol": "Ru", "Z": 44, "n": 5, "ionization_ev": 7.3605},
            {"symbol": "Rh", "Z": 45, "n": 5, "ionization_ev": 7.4589},
            {"symbol": "Pd", "Z": 46, "n": 5, "ionization_ev": 8.3369},
            {"symbol": "Ag", "Z": 47, "n": 5, "ionization_ev": 7.5762},
            {"symbol": "Cd", "Z": 48, "n": 5, "ionization_ev": 8.9938},
        ],
    },
    "d_5d": {
        "l": 2,
        "cases": [
            {"symbol": "Hf", "Z": 72, "n": 6, "ionization_ev": 6.8251},
            {"symbol": "Ta", "Z": 73, "n": 6, "ionization_ev": 7.5496},
            {"symbol": "W", "Z": 74, "n": 6, "ionization_ev": 7.8640},
            {"symbol": "Re", "Z": 75, "n": 6, "ionization_ev": 7.8335},
            {"symbol": "Os", "Z": 76, "n": 6, "ionization_ev": 8.4382},
            {"symbol": "Ir", "Z": 77, "n": 6, "ionization_ev": 8.9670},
            {"symbol": "Pt", "Z": 78, "n": 6, "ionization_ev": 8.9588},
            {"symbol": "Au", "Z": 79, "n": 6, "ionization_ev": 9.2255},
            {"symbol": "Hg", "Z": 80, "n": 6, "ionization_ev": 10.4375},
        ],
    },
    "f_lanthanide_core": {
        "l": 3,
        "cases": [
            {"symbol": "La", "Z": 57, "n": 6, "ionization_ev": 5.5770},
            {"symbol": "Ce", "Z": 58, "n": 6, "ionization_ev": 5.5387},
            {"symbol": "Pr", "Z": 59, "n": 6, "ionization_ev": 5.4730},
            {"symbol": "Nd", "Z": 60, "n": 6, "ionization_ev": 5.5250},
            {"symbol": "Sm", "Z": 62, "n": 6, "ionization_ev": 5.6440},
            {"symbol": "Gd", "Z": 64, "n": 6, "ionization_ev": 6.1500},
            {"symbol": "Tb", "Z": 65, "n": 6, "ionization_ev": 5.8630},
            {"symbol": "Dy", "Z": 66, "n": 6, "ionization_ev": 5.9390},
            {"symbol": "Ho", "Z": 67, "n": 6, "ionization_ev": 6.0220},
            {"symbol": "Er", "Z": 68, "n": 6, "ionization_ev": 6.1080},
            {"symbol": "Tm", "Z": 69, "n": 6, "ionization_ev": 6.1840},
            {"symbol": "Lu", "Z": 71, "n": 6, "ionization_ev": 5.4280},
        ],
    },
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def linear_fit(xs: list[float], ys: list[float]) -> dict:
    mean_x = statistics.fmean(xs)
    mean_y = statistics.fmean(ys)
    denominator = sum((x - mean_x) ** 2 for x in xs)
    slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denominator if denominator else 0.0
    intercept = mean_y - slope * mean_x
    predictions = [slope * x + intercept for x in xs]
    rmse = math.sqrt(sum((y - p) ** 2 for y, p in zip(ys, predictions)) / len(ys))
    return {"slope": slope, "intercept": intercept, "rmse": rmse}


def evaluate_series(name: str, payload: dict) -> dict:
    cases = []
    zs = []
    zeffs = []
    for case in payload["cases"]:
        zeff = estimate_zeff(case["ionization_ev"], int(case["n"]))
        zs.append(float(case["Z"]))
        zeffs.append(zeff)
        cases.append({**case, "zeff_proxy": round(zeff, 6)})

    fit = linear_fit(zs, zeffs)
    l_value = float(payload["l"]) + 0.5
    normalized_slope = fit["slope"] / l_value if l_value else 0.0

    return {
        "name": name,
        "l": int(payload["l"]),
        "l_plus_half": l_value,
        "slope": fit["slope"],
        "intercept": fit["intercept"],
        "rmse": fit["rmse"],
        "normalized_slope": normalized_slope,
        "case_count": len(cases),
        "cases": cases,
    }


def aggregate_d_block(results: list[dict]) -> dict:
    weights = [item["case_count"] for item in results]
    total_weight = sum(weights)
    slope = sum(item["slope"] * item["case_count"] for item in results) / total_weight
    intercept = sum(item["intercept"] * item["case_count"] for item in results) / total_weight
    rmse = sum(item["rmse"] * item["case_count"] for item in results) / total_weight
    normalized = slope / (results[0]["l_plus_half"] if results else 1.0)
    spread = statistics.pstdev([item["slope"] for item in results]) if len(results) > 1 else 0.0
    return {
        "name": "d_block_mean",
        "l": 2,
        "l_plus_half": 2.5,
        "slope": slope,
        "intercept": intercept,
        "rmse": rmse,
        "normalized_slope": normalized,
        "case_count": total_weight,
        "spread": spread,
        "components": results,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    series_results = {name: evaluate_series(name, payload) for name, payload in SERIES.items()}
    d_block = aggregate_d_block([series_results["d_3d"], series_results["d_4d"], series_results["d_5d"]])

    representatives = [
        series_results["s_alkali"],
        series_results["p_halogen"],
        d_block,
        series_results["f_lanthanide_core"],
    ]

    xs = [item["l_plus_half"] for item in representatives]
    ys = [item["slope"] for item in representatives]
    fit = linear_fit(xs, ys)
    expected_slopes = [fit["slope"] * x + fit["intercept"] for x in xs]
    relative_errors = [abs(y - e) / abs(e) if e else 0.0 for y, e in zip(ys, expected_slopes)]
    normalized_values = [item["normalized_slope"] for item in representatives]

    monotonic = all(later > earlier for earlier, later in zip(ys, ys[1:]))
    normalized_cv = statistics.pstdev(normalized_values) / abs(statistics.fmean(normalized_values)) if len(normalized_values) > 1 else 0.0
    max_relative_error = max(relative_errors)
    d_block_spread = d_block["spread"] / abs(d_block["slope"]) if d_block["slope"] else float("inf")

    if monotonic and max_relative_error <= SLOPE_TOLERANCE and normalized_cv <= SLOPE_TOLERANCE:
        verdict = "supported"
    elif monotonic and max_relative_error <= SLOPE_TOLERANCE * 1.75:
        verdict = "partiel"
    else:
        verdict = "falsifie"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "tolerance": SLOPE_TOLERANCE,
        "monotonic": monotonic,
        "normalized_cv": normalized_cv,
        "max_relative_error": max_relative_error,
        "d_block_spread_ratio": d_block_spread,
        "fit": {
            "slope": fit["slope"],
            "intercept": fit["intercept"],
            "rmse": fit["rmse"],
        },
        "representatives": representatives,
        "series_results": series_results,
        "d_block": d_block,
        "expected_slopes": expected_slopes,
        "relative_errors": relative_errors,
        "falsifiers": [
            "the fitted Zeff slopes do not increase with l",
            "the normalized slopes are not approximately constant",
            "the d-block components are too spread out to define a stable representative slope",
        ],
    }

    json_path = outdir / f"family_l_slope_check_{timestamp}.json"
    txt_path = outdir / f"family_l_slope_check_{timestamp}.txt"
    payload = {**data, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Family l-slope check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"tolerance: {SLOPE_TOLERANCE}",
        f"monotonic: {monotonic}",
        f"normalized_cv: {normalized_cv}",
        f"max_relative_error: {max_relative_error}",
        f"d_block_spread_ratio: {d_block_spread}",
        "",
        "Representatives:",
    ]
    for item, expected, rel_err in zip(representatives, expected_slopes, relative_errors):
        lines.append(
            f"- {item['name']}: l={item['l']} slope={item['slope']:.6f} expected={expected:.6f} rel_err={rel_err:.4f} normalized={item['normalized_slope']:.6f}"
        )
    lines.append("")
    lines.append("d-block components:")
    for item in d_block["components"]:
        lines.append(
            f"- {item['name']}: slope={item['slope']:.6f} normalized={item['normalized_slope']:.6f} rmse={item['rmse']:.6f}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether Zeff slopes scale like A(l + 1/2) across families.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()