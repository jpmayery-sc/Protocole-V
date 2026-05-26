"""Validate the onset of magnetic saturation in a nonlinear response model.

The response is modeled as a smooth saturation curve so the early region is
nearly linear and the high-field region approaches a plateau.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


CASES = [
    {"name": "weak", "field": 0.1, "saturation": 1.6, "scale": 0.6},
    {"name": "medium", "field": 0.8, "saturation": 1.6, "scale": 0.6},
    {"name": "strong", "field": 2.5, "saturation": 1.6, "scale": 0.6},
    {"name": "very_strong", "field": 6.0, "saturation": 1.6, "scale": 0.6},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def magnetization(field: float, saturation: float, scale: float) -> float:
    return saturation * math.tanh(field / scale)


def evaluate_case(case: dict) -> dict:
    response = magnetization(case["field"], case["saturation"], case["scale"])
    linear_baseline = (case["saturation"] / case["scale"]) * case["field"]
    return {
        **case,
        "magnetization": response,
        "linear_baseline": linear_baseline,
        "plateau_gap": case["saturation"] - response,
        "relative_gap": (case["saturation"] - response) / case["saturation"],
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    monotone_ok = all(b["magnetization"] > a["magnetization"] for a, b in zip(evaluated[:-1], evaluated[1:]))
    saturation_ok = evaluated[-1]["relative_gap"] < evaluated[0]["relative_gap"]
    plateau_ok = evaluated[-1]["plateau_gap"] < 0.2 * evaluated[-1]["saturation"]

    verdict = "supported" if monotone_ok and saturation_ok and plateau_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "monotone_ok": monotone_ok,
        "saturation_ok": saturation_ok,
        "plateau_ok": plateau_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"strong_nonlinear_magnetic_response_check_{timestamp}.json"
    txt_path = outdir / f"strong_nonlinear_magnetic_response_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Strong nonlinear magnetic response check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"monotone_ok: {monotone_ok}",
        f"saturation_ok: {saturation_ok}",
        f"plateau_ok: {plateau_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: field={case['field']:.2f} M={case['magnetization']:.6f} baseline={case['linear_baseline']:.6f} gap={case['plateau_gap']:.6f}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the nonlinear magnetic saturation response.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()