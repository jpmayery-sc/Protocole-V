"""Heavy border control check for Fr / Ra / Lr.

The goal is not to fit a new law, but to check that the border between the
heavy alkali-like, alkaline-earth-like and D3-like readings remains distinct.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


R_H_EV = 13.6

CASES = [
    {"symbol": "Fr", "family": "alkali_border", "period": 7, "radius_pm": 270.0, "ionization_ev": 4.0727},
    {"symbol": "Ra", "family": "alkaline_earth_border", "period": 7, "radius_pm": 221.0, "ionization_ev": 5.2784},
    {"symbol": "Lr", "family": "d3_border", "period": 7, "radius_pm": 171.0, "ionization_ev": 4.96},
]


def estimate_zeff(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def classify(border_index: float, radius_pm: float) -> str:
    if border_index >= 79.0 or radius_pm >= 250.0:
        return "alkali_like"
    if border_index >= 49.0 or radius_pm >= 200.0:
        return "alkaline_earth_like"
    return "d3_like"


def analyze_cases() -> dict:
    rows = []
    border_classes = []
    for item in CASES:
        zeff = estimate_zeff(item["ionization_ev"], item["period"])
        border_index = item["radius_pm"] / zeff
        border_class = classify(border_index, item["radius_pm"])
        border_classes.append(border_class)
        rows.append(
            {
                **item,
                "zeff_proxy": round(zeff, 6),
                "border_index": round(border_index, 6),
                "border_class": border_class,
            }
        )

    order_ok = [row["symbol"] for row in rows] == ["Fr", "Ra", "Lr"]
    separation_ok = len(set(border_classes)) == len(border_classes)
    border_gradient_ok = rows[0]["border_index"] > rows[1]["border_index"] > rows[2]["border_index"]
    verdict = "supported" if order_ok and separation_ok and border_gradient_ok else "contradicted"

    return {
        "hypothesis": "Fr / Ra / Lr must remain separated at the heavy border and not collapse into one class",
        "case_control": "Fr -> Ra -> Lr",
        "observable": "border index, coarse border class and monotone separation",
        "expected": {
            "Fr": "alkali_like",
            "Ra": "alkaline_earth_like",
            "Lr": "d3_like",
        },
        "cases": rows,
        "criteria": {
            "order_ok": order_ok,
            "separation_ok": separation_ok,
            "border_gradient_ok": border_gradient_ok,
        },
        "verdict": verdict,
        "falsifiers": [
            "Fr, Ra and Lr collapse into a single border class",
            "the border index does not decrease from Fr to Lr",
            "the heavy border cannot distinguish alkaline-earth-like and D3-like readings",
        ],
    }


def write_report(results: dict, outdir: Path) -> tuple[Path, Path]:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    outdir.mkdir(parents=True, exist_ok=True)

    json_path = outdir / f"heavy_border_control_check_{timestamp}.json"
    txt_path = outdir / f"heavy_border_control_check_{timestamp}.txt"
    payload = {"timestamp": timestamp, **results, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Heavy border control check",
        f"timestamp: {timestamp}",
        f"verdict: {results['verdict']}",
        f"order_ok: {results['criteria']['order_ok']}",
        f"separation_ok: {results['criteria']['separation_ok']}",
        f"border_gradient_ok: {results['criteria']['border_gradient_ok']}",
        "",
        "Cases:",
    ]
    for item in results["cases"]:
        lines.append(
            f"- {item['symbol']}: zeff={item['zeff_proxy']:.6f} border_index={item['border_index']:.6f} class={item['border_class']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the heavy border control check.")
    _ = parser.parse_args()

    results = analyze_cases()
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "heavy_border"
    json_path, txt_path = write_report(results, outdir)

    payload = {"json_path": str(json_path), "txt_path": str(txt_path), **results}
    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()