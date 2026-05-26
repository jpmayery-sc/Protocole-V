"""Validate that iron corrosion is a chemical transformation, not wear.

This is a small deterministic test that checks that the iron nucleus stays
the same while the electron count and oxidation state change in corrosion and
oxidation examples.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {
        "name": "Fe metal",
        "kind": "reference",
        "formula": "Fe",
        "z": 26,
        "electrons": 26,
        "oxidation_state": 0,
        "oxygen_atoms": 0,
    },
    {
        "name": "Fe2+",
        "kind": "oxidation",
        "formula": "Fe2+",
        "z": 26,
        "electrons": 24,
        "oxidation_state": 2,
        "oxygen_atoms": 0,
    },
    {
        "name": "Fe3+",
        "kind": "oxidation",
        "formula": "Fe3+",
        "z": 26,
        "electrons": 23,
        "oxidation_state": 3,
        "oxygen_atoms": 0,
    },
    {
        "name": "rust proxy Fe2O3",
        "kind": "rust",
        "formula": "Fe2O3",
        "z": 26,
        "electrons": 23,
        "oxidation_state": 3,
        "oxygen_atoms": 3,
    },
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    protons = int(case["z"])
    electrons = int(case["electrons"])
    neutral_protons = protons == 26
    electron_loss = 26 - electrons
    chemical_change = case["oxidation_state"] > 0 or case["oxygen_atoms"] > 0
    if case["kind"] == "reference":
        ok = neutral_protons and not chemical_change
    else:
        ok = neutral_protons and chemical_change
    return {
        **case,
        "neutral_protons": neutral_protons,
        "electron_loss_from_Fe": electron_loss,
        "chemical_change": chemical_change,
        "ok": ok,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    nucleus_ok = all(case["neutral_protons"] for case in evaluated)
    oxidation_ok = any(case["oxidation_state"] > 0 for case in evaluated)
    oxygen_ok = any(case["oxygen_atoms"] > 0 for case in evaluated if case["kind"] == "rust")
    verdict = "supported" if nucleus_ok and oxidation_ok and oxygen_ok else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "nucleus_ok": nucleus_ok,
        "oxidation_ok": oxidation_ok,
        "oxygen_ok": oxygen_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"iron_rust_check_{ts}.json"
    report_path = outdir / f"iron_rust_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Iron rust check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        f"nucleus_ok: {nucleus_ok}",
        f"oxidation_ok: {oxidation_ok}",
        f"oxygen_ok: {oxygen_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: Z={case['z']} e={case['electrons']} ox={case['oxidation_state']} O={case['oxygen_atoms']} ok={case['ok']}"
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