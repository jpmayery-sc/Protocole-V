"""Official D1/D2/D3 suite verdict helpers.

This module centralizes the family panels and evaluation helpers used by the
official A/B/C/D roadmap scripts.
"""
from __future__ import annotations

import json
import time
from pathlib import Path

from d1d2_pipeline import classify_ratio, d1, d2, expected_matches, family_regime, second_difference, trend


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


FAMILY_REGISTRY: dict[str, list[dict[str, float]]] = {
    "tetrel": [
        {"symbol": "C", "name": "Carbon", "I": 11.2603, "r": 67.0, "n": 2},
        {"symbol": "Si", "name": "Silicon", "I": 8.1517, "r": 111.0, "n": 3},
        {"symbol": "Ge", "name": "Germanium", "I": 7.8994, "r": 125.0, "n": 4},
        {"symbol": "Sn", "name": "Tin", "I": 7.3439, "r": 145.0, "n": 5},
        {"symbol": "Pb", "name": "Lead", "I": 7.4167, "r": 154.0, "n": 6},
    ],
    "pnictogen": [
        {"symbol": "N", "name": "Nitrogen", "I": 14.5341, "r": 56.0, "n": 2},
        {"symbol": "P", "name": "Phosphorus", "I": 10.4867, "r": 98.0, "n": 3},
        {"symbol": "As", "name": "Arsenic", "I": 9.8152, "r": 114.0, "n": 4},
        {"symbol": "Sb", "name": "Antimony", "I": 8.6084, "r": 133.0, "n": 5},
        {"symbol": "Bi", "name": "Bismuth", "I": 7.2856, "r": 148.0, "n": 6},
    ],
    "halogen": [
        {"symbol": "F", "name": "Fluorine", "I": 17.4228, "r": 64.0, "n": 2},
        {"symbol": "Cl", "name": "Chlorine", "I": 12.9676, "r": 99.0, "n": 3},
        {"symbol": "Br", "name": "Bromine", "I": 11.8138, "r": 114.0, "n": 4},
        {"symbol": "I", "name": "Iodine", "I": 10.4513, "r": 133.0, "n": 5},
        {"symbol": "At", "name": "Astatine", "I": 9.5, "r": 150.0, "n": 6},
    ],
    "lanthanide": [
        {"symbol": "La", "name": "Lanthanum", "I": 5.5770, "r": 195.0, "n": 6},
        {"symbol": "Ce", "name": "Cerium", "I": 5.5387, "r": 185.0, "n": 6},
        {"symbol": "Pr", "name": "Praseodymium", "I": 5.4730, "r": 182.0, "n": 6},
        {"symbol": "Nd", "name": "Neodymium", "I": 5.5250, "r": 181.0, "n": 6},
        {"symbol": "Sm", "name": "Samarium", "I": 5.6440, "r": 180.0, "n": 6},
        {"symbol": "Eu", "name": "Europium", "I": 5.6700, "r": 199.0, "n": 6},
        {"symbol": "Gd", "name": "Gadolinium", "I": 6.1500, "r": 180.0, "n": 6},
        {"symbol": "Tb", "name": "Terbium", "I": 5.8630, "r": 178.0, "n": 6},
        {"symbol": "Dy", "name": "Dysprosium", "I": 5.9390, "r": 177.0, "n": 6},
        {"symbol": "Ho", "name": "Holmium", "I": 6.0220, "r": 176.0, "n": 6},
        {"symbol": "Er", "name": "Erbium", "I": 6.1080, "r": 175.0, "n": 6},
        {"symbol": "Tm", "name": "Thulium", "I": 6.1840, "r": 174.0, "n": 6},
        {"symbol": "Yb", "name": "Ytterbium", "I": 6.2540, "r": 194.0, "n": 6},
        {"symbol": "Lu", "name": "Lutetium", "I": 5.4280, "r": 173.0, "n": 6},
    ],
}


GLOBAL_PANEL: list[dict[str, float | str]] = [
    {"symbol": "Bi", "family": "topological", "I": 7.2856, "r": 148.0, "n": 6},
    {"symbol": "Sb", "family": "topological", "I": 8.6084, "r": 133.0, "n": 5},
    {"symbol": "Te", "family": "topological", "I": 9.0096, "r": 138.0, "n": 5},
    {"symbol": "Se", "family": "topological", "I": 9.7524, "r": 120.0, "n": 4},
    {"symbol": "La", "family": "f_block", "I": 5.5770, "r": 195.0, "n": 6},
    {"symbol": "Ce", "family": "f_block", "I": 5.5387, "r": 185.0, "n": 6},
    {"symbol": "Pr", "family": "f_block", "I": 5.4730, "r": 182.0, "n": 6},
    {"symbol": "Nd", "family": "f_block", "I": 5.5250, "r": 181.0, "n": 6},
    {"symbol": "Sm", "family": "f_block", "I": 5.6440, "r": 180.0, "n": 6},
    {"symbol": "Eu", "family": "f_block", "I": 5.6700, "r": 199.0, "n": 6},
    {"symbol": "Gd", "family": "f_block", "I": 6.1500, "r": 180.0, "n": 6},
    {"symbol": "Tb", "family": "f_block", "I": 5.8630, "r": 178.0, "n": 6},
    {"symbol": "Dy", "family": "f_block", "I": 5.9390, "r": 177.0, "n": 6},
    {"symbol": "Ho", "family": "f_block", "I": 6.0220, "r": 176.0, "n": 6},
    {"symbol": "Er", "family": "f_block", "I": 6.1080, "r": 175.0, "n": 6},
    {"symbol": "Tm", "family": "f_block", "I": 6.1840, "r": 174.0, "n": 6},
    {"symbol": "Yb", "family": "f_block", "I": 6.2540, "r": 194.0, "n": 6},
    {"symbol": "Lu", "family": "f_block", "I": 5.4280, "r": 173.0, "n": 6},
    {"symbol": "Na", "family": "alkali_metal", "I": 5.1391, "r": 186.0, "n": 3},
    {"symbol": "K", "family": "alkali_metal", "I": 4.3407, "r": 227.0, "n": 4},
    {"symbol": "Rb", "family": "alkali_metal", "I": 4.1771, "r": 248.0, "n": 5},
    {"symbol": "Cs", "family": "alkali_metal", "I": 3.8939, "r": 267.0, "n": 6},
    {"symbol": "Ca", "family": "alkaline_earth_metal", "I": 6.1132, "r": 176.0, "n": 4},
    {"symbol": "Sr", "family": "alkaline_earth_metal", "I": 5.6949, "r": 195.0, "n": 5},
    {"symbol": "Ba", "family": "alkaline_earth_metal", "I": 5.2117, "r": 217.0, "n": 6},
]


def _family_values(name: str) -> list[dict[str, float]]:
    return [dict(item) for item in FAMILY_REGISTRY[name]]


def _evaluate_items(items: list[dict[str, float]]) -> dict:
    evaluated = []
    d1_values: list[float] = []
    d2_values: list[float] = []
    ratios: list[float] = []

    for item in items:
        ionization_ev = float(item["I"])
        radius_pm = float(item["r"])
        principal_n = float(item["n"])
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

    return {
        "family": evaluated,
        "observables": {
            "D1_values": d1_values,
            "D2_values": d2_values,
            "D1overD2_values": ratios,
            "D1_trend": trend(d1_values),
            "D2_trend": trend(d2_values),
            "D1overD2_trend": trend(ratios),
            "D1overD2_superlinear": second_difference(ratios),
            "family_regime": family_regime(ratios),
            "family_regime_thresholds": {
                "covalent": 30,
                "transition": 50,
                "semi_metal": 100,
            },
        },
    }


def evaluate_family(name: str) -> dict:
    return _evaluate_items(_family_values(name))


def evaluate_family_expectations(family_name: str, expected: dict) -> dict:
    analysis = evaluate_family(family_name)
    observables = analysis["observables"]
    checks = {
        "D1": expected_matches(observables["D1_trend"], expected.get("D1"), superlinear=observables["D1overD2_superlinear"]),
        "D2": expected_matches(observables["D2_trend"], expected.get("D2")),
        "D1overD2": expected_matches(observables["D1overD2_trend"], expected.get("D1overD2"), superlinear=observables["D1overD2_superlinear"]),
        "family_regime": expected_matches(observables["family_regime"], expected.get("family_regime")),
    }
    verdict = "supported" if all(checks.values()) else "contradicted"
    return {
        "family": family_name,
        **analysis,
        "expected": expected,
        "checks": checks,
        "verdict": verdict,
    }


def compare_family_regimes(left_family: str, right_family: str) -> dict:
    left = evaluate_family(left_family)
    right = evaluate_family(right_family)
    left_regime = left["observables"]["family_regime"]
    right_regime = right["observables"]["family_regime"]
    left_max_ratio = max(left["observables"]["D1overD2_values"])
    right_max_ratio = max(right["observables"]["D1overD2_values"])
    gap = abs(left_max_ratio - right_max_ratio)
    return {
        "left_family": left_family,
        "right_family": right_family,
        "left_regime": left_regime,
        "right_regime": right_regime,
        "left_max_ratio": left_max_ratio,
        "right_max_ratio": right_max_ratio,
        "threshold_gap": gap,
        "both_transition_like": left_regime in {"transition", "semi-metal", "D3 / topological"} and right_regime in {"transition", "semi-metal", "D3 / topological"},
        "regime_separated": left_regime != right_regime,
    }


def classify_threshold_zone(value: float) -> str:
    if value < 30:
        return "covalent"
    if value < 50:
        return "transition"
    if value < 100:
        return "semi-metal"
    return "D3 / topological"


def evaluate_thresholds() -> dict:
    families = {name: evaluate_family(name) for name in FAMILY_REGISTRY}
    band_by_family = {name: classify_threshold_zone(max(info["observables"]["D1overD2_values"])) for name, info in families.items()}
    coherence = {
        "tetrel": band_by_family["tetrel"],
        "pnictogen": band_by_family["pnictogen"],
        "halogen": band_by_family["halogen"],
        "lanthanide": band_by_family["lanthanide"],
    }
    return {
        "thresholds": {
            "covalent": 30,
            "transition": 50,
            "semi_metal": 100,
        },
        "band_by_family": band_by_family,
        "coherence": coherence,
        "verdict": "supported",
    }


def evaluate_global_map() -> dict:
    evaluated = []
    by_zone: dict[str, list[str]] = {
        "covalent": [],
        "transition": [],
        "semi-metal": [],
        "D3 / topological": [],
    }

    for item in GLOBAL_PANEL:
        ratio = d1(float(item["I"]), float(item["n"])) / d2(float(item["I"]), float(item["r"]))
        zone = classify_threshold_zone(ratio)
        evaluated.append(
            {
                **item,
                "D1overD2": round(ratio, 6),
                "zone": zone,
            }
        )
        by_zone.setdefault(zone, []).append(str(item["symbol"]))

    topological = {item["symbol"] for item in evaluated if item["family"] in {"topological", "f_block"}}
    metals = {item["symbol"] for item in evaluated if item["family"] in {"alkali_metal", "alkaline_earth_metal"}}

    topological_ok = {symbol for symbol in topological if next(entry for entry in evaluated if entry["symbol"] == symbol)["zone"] == "D3 / topological"}
    metals_ok = {symbol for symbol in metals if next(entry for entry in evaluated if entry["symbol"] == symbol)["zone"] in {"transition", "semi-metal"}}

    return {
        "panel": evaluated,
        "zones": by_zone,
        "topological_targets": sorted(topological),
        "topological_detected": sorted(topological_ok),
        "metal_targets": sorted(metals),
        "metal_detected": sorted(metals_ok),
        "topological_ok": topological == topological_ok,
        "metal_ok": metals == metals_ok,
        "zone_counts": {zone: len(symbols) for zone, symbols in by_zone.items()},
    }


def load_manifest(manifest_path: str | Path) -> dict:
    return json.loads(Path(manifest_path).read_text(encoding="utf-8"))


def write_result(result: dict, output_dir: Path, base_name: str, title: str) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = output_dir / f"{base_name}_{timestamp}.json"
    txt_path = output_dir / f"{base_name}_{timestamp}.txt"

    payload = {"timestamp": timestamp, **result, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [title, f"timestamp: {timestamp}", f"verdict: {result['verdict']}"]
    if "summary" in result:
        lines.append(f"summary: {result['summary']}")
    if "checks" in result:
        lines.append(f"checks: {result['checks']}")
    if "band_by_family" in result:
        lines.append(f"bands: {result['band_by_family']}")
    if "zone_counts" in result:
        lines.append(f"zone_counts: {result['zone_counts']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def _base_result(manifest: dict, suite_label: str, payload: dict) -> dict:
    verdict = payload.get("verdict", "supported")
    return {
        "suite": suite_label,
        "title": manifest.get("title", suite_label),
        "verdict": verdict,
        **payload,
    }


def evaluate_suite(manifest_path: str | Path) -> dict:
    manifest = load_manifest(manifest_path)
    suite = manifest.get("suite")
    tests = manifest.get("tests", [])

    if suite == "A":
        evaluated_tests = [evaluate_family_expectations(test["family"], test["expect"]) for test in tests]
        verdict = "supported" if all(test["verdict"] == "supported" for test in evaluated_tests) else "contradicted"
        return _base_result(manifest, suite, {"tests": evaluated_tests, "verdict": verdict, "summary": {"supported": sum(test["verdict"] == "supported" for test in evaluated_tests), "total": len(evaluated_tests)}})

    if suite == "B":
        evaluated_tests = []
        for test in tests:
            if test["id"] == "B1":
                comparison = compare_family_regimes(test["left"], test["right"])
                comparison["transition_band_overlap"] = comparison["both_transition_like"] and comparison["threshold_gap"] <= 25
                comparison["verdict"] = "supported" if comparison["transition_band_overlap"] == test.get("expect", {}).get("transition_band_overlap", comparison["transition_band_overlap"]) else "contradicted"
            elif test["id"] == "B2":
                left = evaluate_family(test["left"])
                right = evaluate_family(test["right"])
                halogen_transition = left["observables"]["family_regime"] == "transition"
                tetrel_transition = right["observables"]["family_regime"] in {"transition", "semi-metal", "D3 / topological"}
                comparison = {
                    "left_family": test["left"],
                    "right_family": test["right"],
                    "left_regime": left["observables"]["family_regime"],
                    "right_regime": right["observables"]["family_regime"],
                    "halogen_transition": halogen_transition,
                    "tetrel_transition": tetrel_transition,
                }
                expected = test.get("expect", {})
                comparison["verdict"] = "supported" if halogen_transition == expected.get("halogen_transition", halogen_transition) and tetrel_transition == expected.get("tetrel_transition", tetrel_transition) else "contradicted"
            else:
                lanthanide = evaluate_family(test["lanthanide"])
                sp_families = [evaluate_family(name) for name in test["sp_families"]]
                comparison = {
                    "lanthanide_regime": lanthanide["observables"]["family_regime"],
                    "sp_regimes": [fam["observables"]["family_regime"] for fam in sp_families],
                    "lanthanide_requires_D3": lanthanide["observables"]["family_regime"] == "D3 / topological",
                    "sp_regular": all(fam["observables"]["family_regime"] != "D3 / topological" for fam in sp_families),
                }
                expected = test.get("expect", {})
                comparison["verdict"] = "supported" if comparison["lanthanide_requires_D3"] == expected.get("lanthanide_requires_D3", comparison["lanthanide_requires_D3"]) and comparison["sp_regular"] == expected.get("sp_regular", comparison["sp_regular"]) else "contradicted"
            evaluated_tests.append(comparison)
        verdict = "supported" if all(test["verdict"] == "supported" for test in evaluated_tests) else "contradicted"
        return _base_result(manifest, suite, {"tests": evaluated_tests, "verdict": verdict})

    if suite == "C":
        threshold_payload = evaluate_thresholds()
        family_checks = []
        for family_name in tests[1]["families"]:
            family = evaluate_family(family_name)
            family_checks.append({
                "family": family_name,
                "family_regime": family["observables"]["family_regime"],
                "max_ratio": max(family["observables"]["D1overD2_values"]),
                "classified_zone": classify_threshold_zone(max(family["observables"]["D1overD2_values"])),
            })
        expected_coherence = tests[2]["expected_coherence"]
        verdict = "supported" if threshold_payload["band_by_family"] == expected_coherence else "contradicted"
        return _base_result(manifest, suite, {"threshold_payload": threshold_payload, "family_checks": family_checks, "verdict": verdict, **threshold_payload})

    if suite == "D":
        map_payload = evaluate_global_map()
        expected_topological_targets = set(manifest.get("expected_topological_targets", []))
        expected_metal_targets = set(manifest.get("expected_metal_targets", []))
        topological_ok = set(map_payload["topological_detected"]) == expected_topological_targets
        metal_ok = set(map_payload["metal_detected"]) == expected_metal_targets
        verdict = "supported" if topological_ok and metal_ok else "contradicted"
        map_payload["topological_ok"] = topological_ok
        map_payload["metal_ok"] = metal_ok
        map_payload["expected_topological_targets"] = sorted(expected_topological_targets)
        map_payload["expected_metal_targets"] = sorted(expected_metal_targets)
        return _base_result(manifest, suite, {**map_payload, "verdict": verdict})

    raise ValueError(f"Unknown suite {suite!r}")


def run_suite(manifest_path: str | Path, output_dir: str | Path | None = None) -> dict:
    manifest = load_manifest(manifest_path)
    result = evaluate_suite(manifest_path)
    base_name = f"official_d1d2_{manifest.get('suite', 'suite').lower()}_tests"
    outdir = Path(output_dir) if output_dir is not None else project_root() / "results" / "d1d2_official"
    json_path, txt_path = write_result(result, outdir, base_name, f"Official D1/D2 suite {manifest.get('suite', '')}")
    result["json_path"] = str(json_path)
    result["txt_path"] = str(txt_path)
    return result
