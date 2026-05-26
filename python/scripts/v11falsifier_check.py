"""Check whether the V11 redshift model stays within conservative falsification bounds."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v11atom_check import evaluate_internal_redshift
from v11canal_check import evaluate_channel_redshift
from v11geo_check import evaluate_geometric_redshift
from v11total_check import evaluate_total_redshift


BOUNDS = {
    "geo": {"min": 1.0e-7, "max": 2.0e-6},
    "atom": {"min": 1.0e-7, "max": 1.0e-5},
    "canal": {"min": 5.0e-7, "max": 5.0e-6},
    "total": {"min": 1.0e-6, "max": 1.0e-5},
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def check_series(series: list[float], lower: float, upper: float) -> dict:
    in_bounds = all(lower <= value <= upper for value in series)
    monotone_ok = all(later > earlier for earlier, later in zip(series, series[1:]))
    sign_ok = all(value > 0.0 for value in series)
    supported = in_bounds and monotone_ok and sign_ok
    if supported:
        verdict = "conforme"
    else:
        verdict = "falsifie" if (not sign_ok or not monotone_ok or not in_bounds) else "partiel"

    return {
        "series": series,
        "lower": lower,
        "upper": upper,
        "in_bounds": in_bounds,
        "monotone_ok": monotone_ok,
        "sign_ok": sign_ok,
        "supported": supported,
        "verdict": verdict,
    }


def evaluate_falsification() -> dict:
    geo_result = evaluate_geometric_redshift()
    atom_result = evaluate_internal_redshift()
    canal_result = evaluate_channel_redshift()
    total_result = evaluate_total_redshift()

    geo_nominal = [case["nominal_redshift"] for case in geo_result["cases"]]
    atom_nominal = [case["nominal_redshift"] for case in atom_result["cases"]]
    canal_nominal = [case["nominal_redshift"] for case in canal_result["cases"]]
    total_nominal = [case["nominal_z_mod"] for case in total_result["cases"]]

    geo_check = check_series(geo_nominal, BOUNDS["geo"]["min"], BOUNDS["geo"]["max"])
    atom_check = check_series(atom_nominal, BOUNDS["atom"]["min"], BOUNDS["atom"]["max"])
    canal_check = check_series(canal_nominal, BOUNDS["canal"]["min"], BOUNDS["canal"]["max"])
    total_check = check_series(total_nominal, BOUNDS["total"]["min"], BOUNDS["total"]["max"])

    block_checks = {
        "geo": geo_check,
        "atom": atom_check,
        "canal": canal_check,
        "total": total_check,
    }
    supported_count = sum(1 for item in block_checks.values() if item["supported"])
    falsified_count = sum(1 for item in block_checks.values() if item["verdict"] == "falsifie")

    if supported_count == len(block_checks):
        overall_verdict = "conforme"
    elif falsified_count > 0:
        overall_verdict = "falsifie"
    else:
        overall_verdict = "partiel"

    return {
        "bounds": BOUNDS,
        "block_checks": block_checks,
        "supported_count": supported_count,
        "total_count": len(block_checks),
        "falsified_count": falsified_count,
        "overall_verdict": overall_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_falsification()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "les redshifts V11 doivent rester petits, positifs et ordonnes dans des bornes conservatrices",
        "case_control": "geo, atom, canal, total",
        "observable": "z_geo, z_int, z_canal, z_mod",
        "expected": "conforme si les quatre blocs restent dans les bornes, partiel sinon, falsifie si un bloc sort de la fenetre",
        "measured": {
            "supported_count": result["supported_count"],
            "total_count": result["total_count"],
            "falsified_count": result["falsified_count"],
        },
        "bounds": result["bounds"],
        "block_checks": result["block_checks"],
        "verdict": result["overall_verdict"],
        "reference": "V11 GEO, ATOM, CANAL and TOTAL blocks",
    }

    json_path = outdir / f"v11falsifier_check_{timestamp}.json"
    txt_path = outdir / f"v11falsifier_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V11 falsification check",
        f"timestamp: {timestamp}",
        f"verdict: {result['overall_verdict']}",
        f"supported_count: {result['supported_count']}/{result['total_count']}",
        f"falsified_count: {result['falsified_count']}",
        "",
        "Blocks:",
    ]
    for label, check in result["block_checks"].items():
        lines.append(
            f"- {label}: {check['verdict']} | in_bounds={check['in_bounds']} | monotone_ok={check['monotone_ok']} | sign_ok={check['sign_ok']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check whether the V11 redshift model stays inside conservative falsification bounds.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()