"""Validate that isotopes preserve element identity while changing mass and sometimes stability.

The check is deterministic and intentionally small so it can run without external data.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {"name": "C-12", "element": "C", "atomic_number": 6, "mass_number": 12, "stable": True},
    {"name": "C-13", "element": "C", "atomic_number": 6, "mass_number": 13, "stable": True},
    {"name": "C-14", "element": "C", "atomic_number": 6, "mass_number": 14, "stable": False},
    {"name": "Cl-35", "element": "Cl", "atomic_number": 17, "mass_number": 35, "stable": True},
    {"name": "Cl-37", "element": "Cl", "atomic_number": 17, "mass_number": 37, "stable": True},
    {"name": "U-238", "element": "U", "atomic_number": 92, "mass_number": 238, "stable": False},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    atomic_number = int(case["atomic_number"])
    mass_number = int(case["mass_number"])
    neutron_number = mass_number - atomic_number
    identity_ok = atomic_number > 0 and mass_number > atomic_number
    return {
        **case,
        "neutron_number": neutron_number,
        "identity_ok": identity_ok,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    same_element_groups = {
        "C": [case for case in evaluated if case["element"] == "C"],
        "Cl": [case for case in evaluated if case["element"] == "Cl"],
    }

    identity_ok = all(case["identity_ok"] for case in evaluated)
    mass_varies = any(case["mass_number"] != evaluated[0]["mass_number"] for case in evaluated)
    stability_differs = any(case["stable"] is False for case in evaluated)
    same_element_ok = all(len(group) >= 2 and len({case["atomic_number"] for case in group}) == 1 for group in same_element_groups.values())

    verdict = "supported" if identity_ok and mass_varies and stability_differs and same_element_ok else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "identity_ok": identity_ok,
        "mass_varies": mass_varies,
        "stability_differs": stability_differs,
        "same_element_ok": same_element_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"isotope_check_{ts}.json"
    report_path = outdir / f"isotope_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Isotope check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        f"identity_ok: {identity_ok}",
        f"mass_varies: {mass_varies}",
        f"stability_differs: {stability_differs}",
        f"same_element_ok: {same_element_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: Z={case['atomic_number']} A={case['mass_number']} N={case['neutron_number']} stable={case['stable']} identity_ok={case['identity_ok']}"
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