"""Generic D1/D2 pipeline for atom-family JSON fixtures.

The script reads a standardized JSON family, computes D1, D2 and D1/D2 for
each member, classifies the family regime, and writes a result JSON/TXT pair.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics as stats
import time
from pathlib import Path


R_H_EV = 13.6


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def get_field(item: dict, primary: str, fallback: str) -> float:
    if primary in item:
        return float(item[primary])
    return float(item[fallback])


def d1(ionization_ev: float, principal_n: float) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / R_H_EV)


def d2(ionization_ev: float, radius_pm: float) -> float:
    return ionization_ev / radius_pm


def trend(values: list[float]) -> str:
    if len(values) < 2:
        return "flat"
    if all(b > a for a, b in zip(values[:-1], values[1:])):
        return "increasing"
    if all(b < a for a, b in zip(values[:-1], values[1:])):
        return "decreasing"
    return "mixed"


def second_difference(values: list[float]) -> bool:
    if len(values) < 3:
        return False
    steps = [b - a for a, b in zip(values[:-1], values[1:])]
    return all(next_step >= current_step for current_step, next_step in zip(steps[:-1], steps[1:]))


def expected_matches(actual: str, expected_text: str | None, *, superlinear: bool = False) -> bool:
    if not expected_text:
        return True

    normalized = expected_text.lower()
    actual_normalized = actual.lower()
    if "super" in normalized:
        return actual_normalized == "increasing" and superlinear
    if "monotonic increase" in normalized or normalized == "increasing" or "increasing" in normalized:
        return actual_normalized == "increasing"
    if "monotonic decrease" in normalized or normalized == "decreasing" or "decreasing" in normalized:
        return actual_normalized == "decreasing"
    if "mixed" in normalized:
        return actual_normalized == "mixed"
    return actual_normalized == normalized


def classify_ratio(value: float) -> str:
    if value < 30:
        return "covalent"
    if value < 50:
        return "transition"
    if value < 100:
        return "semi-metal"
    return "D3 / topological"


def family_regime(ratios: list[float]) -> str:
    if not ratios:
        return "unknown"
    return classify_ratio(max(ratios))


def load_config(json_path: str | Path) -> dict:
    return json.loads(Path(json_path).read_text(encoding="utf-8"))


def analyze_family(config: dict) -> dict:
    evaluated = []
    d1_values = []
    d2_values = []
    ratios = []

    for item in config["family"]:
        ionization_ev = get_field(item, "I", "ionization_ev")
        radius_pm = get_field(item, "r", "radius_pm")
        principal_n = get_field(item, "n", "period")

        value_d1 = d1(ionization_ev, principal_n)
        value_d2 = d2(ionization_ev, radius_pm)
        ratio = value_d1 / value_d2 if value_d2 else float("inf")

        evaluated.append(
            {
                **item,
                "I": ionization_ev,
                "r": radius_pm,
                "n": principal_n,
                "D1": round(value_d1, 6),
                "D2": round(value_d2, 6),
                "D1overD2": round(ratio, 6),
                "regime": classify_ratio(ratio),
            }
        )
        d1_values.append(value_d1)
        d2_values.append(value_d2)
        ratios.append(ratio)

    d1_trend = trend(d1_values)
    d2_trend = trend(d2_values)
    ratio_trend = trend(ratios)
    ratio_superlinear = second_difference(ratios)

    expected = config.get("expected", {})
    family_regime_value = family_regime(ratios)

    verdict = "supported"
    checks = {
        "D1": expected_matches(d1_trend, expected.get("D1")),
        "D2": expected_matches(d2_trend, expected.get("D2")),
        "D1overD2": expected_matches(ratio_trend, expected.get("D1overD2"), superlinear=ratio_superlinear),
        "family_regime": expected_matches(family_regime_value, expected.get("family_regime")),
    }
    if not all(checks.values()):
        verdict = "contradicted"

    return {
        "familyname": config.get("familyname") or config.get("family_name"),
        "family_name": config.get("family_name") or config.get("familyname"),
        "family": evaluated,
        "observables": {
            "D1_values": d1_values,
            "D2_values": d2_values,
            "D1overD2_values": ratios,
            "D1_trend": d1_trend,
            "D2_trend": d2_trend,
            "D1overD2_trend": ratio_trend,
            "D1overD2_superlinear": ratio_superlinear,
            "family_regime": family_regime_value,
            "family_regime_thresholds": {
                "covalent": 30,
                "transition": 50,
                "semi_metal": 100,
            },
        },
        "hypothesis": config.get("hypothesis", ""),
        "case_control": config.get("case_control", ""),
        "expected": expected,
        "verdict": verdict,
        "checks": checks,
    }


def write_results(result: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    familyname = result["familyname"]
    json_path = output_dir / f"{familyname}_D1D2_results_{timestamp}.json"
    txt_path = output_dir / f"{familyname}_D1D2_results_{timestamp}.txt"

    payload = {"timestamp": timestamp, **result, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "D1/D2 family check",
        f"timestamp: {timestamp}",
        f"familyname: {familyname}",
        f"verdict: {result['verdict']}",
        f"family_regime: {result['observables']['family_regime']}",
        f"D1_trend: {result['observables']['D1_trend']}",
        f"D2_trend: {result['observables']['D2_trend']}",
        f"D1overD2_trend: {result['observables']['D1overD2_trend']}",
        f"D1overD2_superlinear: {result['observables']['D1overD2_superlinear']}",
        "",
        "Per element:",
    ]
    for item in result["family"]:
        lines.append(
            f"- {item['symbol']}: I={item['I']:.4f} r={item['r']:.1f} n={item['n']:.0f} D1={item['D1']:.6f} D2={item['D2']:.6f} D1/D2={item['D1overD2']:.6f} regime={item['regime']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def analyze_file(json_path: str | Path, output_dir: str | Path | None = None) -> dict:
    config = load_config(json_path)
    result = analyze_family(config)
    outdir = Path(output_dir) if output_dir is not None else project_root() / "results" / "d1d2"
    json_file, txt_file = write_results(result, outdir)
    result["json_path"] = str(json_file)
    result["txt_path"] = str(txt_file)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Generic D1/D2 pipeline for atom-family JSON fixtures.")
    parser.add_argument("json_path", help="Input family JSON")
    parser.add_argument("--output-dir", default=None, help="Output directory for result files")
    args = parser.parse_args()

    result = analyze_file(args.json_path, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()