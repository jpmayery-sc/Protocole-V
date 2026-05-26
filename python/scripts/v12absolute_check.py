"""Check the V12 absolute bounds on V11 redshift observables."""
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
    "geo": (1.0e-7, 2.0e-6),
    "atom": (1.0e-7, 1.0e-5),
    "canal": (5.0e-7, 5.0e-6),
    "total": (1.0e-6, 1.0e-5),
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def evaluate_absolute_bounds() -> dict:
    geo_result = evaluate_geometric_redshift()
    atom_result = evaluate_internal_redshift()
    canal_result = evaluate_channel_redshift()
    total_result = evaluate_total_redshift()

    series = {
        "geo": [case["nominal_redshift"] for case in geo_result["cases"]],
        "atom": [case["nominal_redshift"] for case in atom_result["cases"]],
        "canal": [case["nominal_redshift"] for case in canal_result["cases"]],
        "total": [case["nominal_z_mod"] for case in total_result["cases"]],
    }

    checks = {}
    for label, values in series.items():
        lower, upper = BOUNDS[label]
        in_bounds = all(lower <= value <= upper for value in values)
        checks[label] = {
            "values": values,
            "lower": lower,
            "upper": upper,
            "in_bounds": in_bounds,
            "monotone_ok": all(later > earlier for earlier, later in zip(values, values[1:])),
            "verdict": "conforme" if in_bounds else "falsifie",
        }

    supported = all(check["verdict"] == "conforme" for check in checks.values())
    verdict = "conforme" if supported else "falsifie"
    return {"checks": checks, "verdict": verdict}


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_absolute_bounds()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "les observables redshift internes de V11 doivent rester dans des bornes conservatrices",
        "case_control": "geo, atom, canal, total",
        "observable": "z_geo, z_int, z_canal, z_mod",
        "expected": "conforme si les valeurs nominales restent dans les bornes, falsifie sinon",
        "measured": {
            label: {
                "values": check["values"],
                "lower": check["lower"],
                "upper": check["upper"],
                "in_bounds": check["in_bounds"],
                "monotone_ok": check["monotone_ok"],
            }
            for label, check in result["checks"].items()
        },
        "verdict": result["verdict"],
        "reference": "V11 GEO, ATOM, CANAL and TOTAL blocks",
    }

    json_path = outdir / f"v12absolute_check_{timestamp}.json"
    txt_path = outdir / f"v12absolute_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V12 absolute bounds check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        "",
        "Blocks:",
    ]
    for label, check in result["checks"].items():
        lines.append(
            f"- {label}: {check['verdict']} | in_bounds={check['in_bounds']} | monotone_ok={check['monotone_ok']} | values={check['values']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check V12 absolute bounds on V11 observables.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()