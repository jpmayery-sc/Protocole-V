"""Validate a simple electron-affinity ordering across representative elements.

The check uses a small, deterministic set of reference values to confirm that
halogens bind an extra electron more strongly than chalcogens and alkali metals,
while noble gases remain near zero or unfavorable.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {"name": "Cl", "group": "halogen", "electron_affinity_ev": 3.61},
    {"name": "F", "group": "halogen", "electron_affinity_ev": 3.40},
    {"name": "O", "group": "chalcogen", "electron_affinity_ev": 1.46},
    {"name": "Na", "group": "alkali", "electron_affinity_ev": 0.55},
    {"name": "Ne", "group": "noble_gas", "electron_affinity_ev": -1.20},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    affinity = float(case["electron_affinity_ev"])
    favorable = affinity > 0.0
    return {
        **case,
        "favorable": favorable,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    by_name = {case["name"]: case for case in evaluated}
    ordering_ok = (
        by_name["Cl"]["electron_affinity_ev"] > by_name["F"]["electron_affinity_ev"] > by_name["O"]["electron_affinity_ev"] > by_name["Na"]["electron_affinity_ev"]
    )
    noble_gas_ok = by_name["Ne"]["electron_affinity_ev"] <= 0.0
    group_sign_ok = (
        by_name["Cl"]["favorable"]
        and by_name["F"]["favorable"]
        and by_name["O"]["favorable"]
        and by_name["Na"]["favorable"]
        and not by_name["Ne"]["favorable"]
    )

    verdict = "supported" if ordering_ok and noble_gas_ok and group_sign_ok else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "ordering_ok": ordering_ok,
        "noble_gas_ok": noble_gas_ok,
        "group_sign_ok": group_sign_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"electron_affinity_check_{ts}.json"
    txt_path = outdir / f"electron_affinity_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Electron affinity check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        f"ordering_ok: {ordering_ok}",
        f"noble_gas_ok: {noble_gas_ok}",
        f"group_sign_ok: {group_sign_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: group={case['group']} affinity_ev={case['electron_affinity_ev']} favorable={case['favorable']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()