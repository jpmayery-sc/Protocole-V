"""Validate the strong induction regime against the weak-field baseline.

The script uses a simple nonlinear response law to capture the idea that the
induced voltage departs from linearity when the field variation becomes large.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


CASES = [
    {"name": "weak", "field_rate": 1.0, "gain": 1.0, "phase": 0.0},
    {"name": "intermediate", "field_rate": 4.0, "gain": 1.0, "phase": 0.0},
    {"name": "strong", "field_rate": 10.0, "gain": 1.0, "phase": 0.0},
    {"name": "very_strong", "field_rate": 18.0, "gain": 1.0, "phase": 0.0},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def induced_voltage(field_rate: float, gain: float) -> float:
    return 2.0 * gain * math.tanh(field_rate / 8.0)


def evaluate_case(case: dict) -> dict:
    linear_prediction = case["gain"] * case["field_rate"]
    voltage = induced_voltage(case["field_rate"], case["gain"])
    return {
        **case,
        "linear_prediction": linear_prediction,
        "induced_voltage": voltage,
        "deviation_from_linear": linear_prediction - voltage,
        "relative_deviation": (linear_prediction - voltage) / linear_prediction if linear_prediction else 0.0,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    weak = evaluated[0]
    strong = evaluated[-1]
    monotone_ok = all(b["induced_voltage"] > a["induced_voltage"] for a, b in zip(evaluated[:-1], evaluated[1:]))
    curvature_ok = strong["relative_deviation"] > weak["relative_deviation"]
    sign_ok = all(case["induced_voltage"] > 0.0 for case in evaluated)

    verdict = "supported" if monotone_ok and curvature_ok and sign_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "monotone_ok": monotone_ok,
        "curvature_ok": curvature_ok,
        "sign_ok": sign_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"strong_induction_check_{timestamp}.json"
    txt_path = outdir / f"strong_induction_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Strong induction check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"monotone_ok: {monotone_ok}",
        f"curvature_ok: {curvature_ok}",
        f"sign_ok: {sign_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: rate={case['field_rate']:.2f} linear={case['linear_prediction']:.6f} induced={case['induced_voltage']:.6f} rel_dev={case['relative_deviation']:.6f}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the strong induction regime.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()