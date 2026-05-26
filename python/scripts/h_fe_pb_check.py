"""Validate the nuclear-stability protocol used in the V4 dossier.

The check is intentionally deterministic and small:
- H-1 is the minimal case with no neutron reserve.
- He-4, C-12 and O-16 build the light-side rising branch.
- Fe-56 is the stability peak.
- Pb-208 and U-238 build the heavy-side falling branch.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


CASES = [
    {"name": "H-1", "label": "H", "protons": 1, "neutrons": 0, "electrons": 1, "binding_energy_per_nucleon_mev": 0.0},
    {"name": "He-4", "label": "He", "protons": 2, "neutrons": 2, "electrons": 2, "binding_energy_per_nucleon_mev": 7.0739},
    {"name": "C-12", "label": "C", "protons": 6, "neutrons": 6, "electrons": 6, "binding_energy_per_nucleon_mev": 7.6801},
    {"name": "O-16", "label": "O", "protons": 8, "neutrons": 8, "electrons": 8, "binding_energy_per_nucleon_mev": 7.9762},
    {"name": "Fe-56", "label": "Fe", "protons": 26, "neutrons": 30, "electrons": 26, "binding_energy_per_nucleon_mev": 8.7904},
    {"name": "Pb-208", "label": "Pb", "protons": 82, "neutrons": 126, "electrons": 82, "binding_energy_per_nucleon_mev": 7.8675},
    {"name": "U-238", "label": "U", "protons": 92, "neutrons": 146, "electrons": 92, "binding_energy_per_nucleon_mev": 7.5701},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    protons = int(case["protons"])
    neutrons = int(case["neutrons"])
    electrons = int(case["electrons"])
    mass_number = protons + neutrons
    charge = protons - electrons
    neutron_to_proton = neutrons / protons if protons else math.nan
    balance_distance = abs(neutron_to_proton - 1.0) if math.isfinite(neutron_to_proton) else math.nan
    return {
        **case,
        "mass_number": mass_number,
        "charge": charge,
        "neutron_to_proton": neutron_to_proton,
        "balance_distance": balance_distance,
        "neutral": charge == 0,
    }


def analyze_curve(evaluated: list[dict]) -> dict:
    ordered = sorted(evaluated, key=lambda case: (case["neutron_to_proton"], case["mass_number"]))
    peak_case = max(ordered, key=lambda case: case["binding_energy_per_nucleon_mev"])
    peak_index = ordered.index(peak_case)
    peak_energy = peak_case["binding_energy_per_nucleon_mev"]

    ordered_case_names = [case["name"] for case in ordered]
    expected_order = ["H-1", "He-4", "C-12", "O-16", "Fe-56", "Pb-208", "U-238"]
    ordered_ok = ordered_case_names == expected_order
    peak_is_fe_ok = peak_case["name"] == "Fe-56"
    light_side_ok = all(case["binding_energy_per_nucleon_mev"] < peak_energy for case in ordered[:peak_index])
    heavy_side_ok = all(case["binding_energy_per_nucleon_mev"] < peak_energy for case in ordered[peak_index + 1 :])

    rising_branch_ok = all(
        ordered[i]["binding_energy_per_nucleon_mev"] <= ordered[i + 1]["binding_energy_per_nucleon_mev"]
        for i in range(peak_index)
    )
    falling_branch_ok = all(
        ordered[i]["binding_energy_per_nucleon_mev"] >= ordered[i + 1]["binding_energy_per_nucleon_mev"]
        for i in range(peak_index, len(ordered) - 1)
    )

    shape_ok = ordered_ok and peak_is_fe_ok and light_side_ok and heavy_side_ok and rising_branch_ok and falling_branch_ok

    return {
        "ordered_cases": ordered,
        "ordered_case_names": ordered_case_names,
        "peak_case": peak_case,
        "peak_index": peak_index,
        "peak_energy": peak_energy,
        "ordered_ok": ordered_ok,
        "peak_is_fe_ok": peak_is_fe_ok,
        "light_side_ok": light_side_ok,
        "heavy_side_ok": heavy_side_ok,
        "rising_branch_ok": rising_branch_ok,
        "falling_branch_ok": falling_branch_ok,
        "shape_ok": shape_ok,
        "shape": "cloche" if shape_ok else "non_cloche",
    }


def run_check(output_dir: str | Path | None = None, stem: str = "h_fe_pb_check") -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]
    by_label = {case["label"]: case for case in evaluated}
    curve = analyze_curve(evaluated)

    h = by_label["H"]
    he = by_label["He"]
    c = by_label["C"]
    o = by_label["O"]
    fe = by_label["Fe"]
    pb = by_label["Pb"]
    u = by_label["U"]

    minimal_ok = h["neutrons"] == 0 and h["neutral"]
    balance_ok = fe["neutral"] and fe["balance_distance"] < h["balance_distance"] and fe["balance_distance"] < pb["balance_distance"]
    heavy_ok = pb["neutral"] and pb["neutrons"] > fe["neutrons"] and pb["balance_distance"] > fe["balance_distance"]
    order_ok = h["neutrons"] < fe["neutrons"] < pb["neutrons"]
    curve_ok = curve["shape_ok"]

    verdict = "supported" if minimal_ok and balance_ok and heavy_ok and order_ok and curve_ok else "contradicted"

    data = {
        "timestamp": ts,
        "hypothesis": "nuclear stability follows a curve with an optimum in N/Z and a peak near Fe-56",
        "case_control": "H-1 -> He-4 -> C-12 -> O-16 -> Fe-56 -> Pb-208 -> U-238",
        "observable": "binding_energy_per_nucleon versus N/Z",
        "expected": "rise on the light side, maximum near Fe-56, then fall on the heavy side",
        "verdict": verdict,
        "minimal_ok": minimal_ok,
        "balance_ok": balance_ok,
        "heavy_ok": heavy_ok,
        "order_ok": order_ok,
        "curve_ok": curve_ok,
        "shape": curve["shape"],
        "ordered_case_names": curve["ordered_case_names"],
        "peak_case": curve["peak_case"],
        "light_side_ok": curve["light_side_ok"],
        "heavy_side_ok": curve["heavy_side_ok"],
        "rising_branch_ok": curve["rising_branch_ok"],
        "falling_branch_ok": curve["falling_branch_ok"],
        "peak_energy": curve["peak_energy"],
        "cases": evaluated,
        "curve_cases": curve["ordered_cases"],
        "falsifiers": [
            "Fe-56 is not the maximum binding-energy-per-nucleon case",
            "the light-side sequence does not rise toward Fe-56",
            "the heavy-side sequence does not fall after Fe-56",
            "the N/Z ordering does not preserve the expected nucleus progression",
        ],
    }

    data["case_control_items"] = [h, he, c, o, fe, pb, u]

    json_path = outdir / f"{stem}_{ts}.json"
    report_path = outdir / f"{stem}_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "H / Fe / Pb check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        f"minimal_ok: {minimal_ok}",
        f"balance_ok: {balance_ok}",
        f"heavy_ok: {heavy_ok}",
        f"order_ok: {order_ok}",
        f"curve_ok: {curve_ok}",
        f"shape: {curve['shape']}",
        f"peak_case: {curve['peak_case']['name']}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: p={case['protons']} n={case['neutrons']} e={case['electrons']} N/Z={case['neutron_to_proton']:.6f} B/A={case['binding_energy_per_nucleon_mev']:.4f} MeV balance_distance={case['balance_distance']:.6f}"
        )
    lines.extend(
        [
            "",
            "Curve order:",
            "- " + " -> ".join(curve["ordered_case_names"]),
            f"- peak_energy: {curve['peak_energy']:.4f} MeV at {curve['peak_case']['name']}",
        ]
    )
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["report_path"] = str(report_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()