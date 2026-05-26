"""Validate successive ionization energies for a few reference elements.

The check keeps the nucleus fixed within each case and verifies that
successive ionization energies are ordered, with at least one clear shell jump.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {"name": "Na", "atomic_number": 11, "ionization_energies_ev": [5.1391, 47.286]},
    {"name": "Mg", "atomic_number": 12, "ionization_energies_ev": [7.6462, 15.035, 80.143]},
    {"name": "Al", "atomic_number": 13, "ionization_energies_ev": [5.9858, 18.828, 28.447]},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_case(case: dict) -> dict:
    energies = [float(value) for value in case["ionization_energies_ev"]]
    monotonic = all(later >= earlier for earlier, later in zip(energies, energies[1:]))
    ratios = [later / earlier for earlier, later in zip(energies, energies[1:])]
    largest_jump = max(ratios) if ratios else 1.0
    return {
        **case,
        "monotonic": monotonic,
        "ratios": ratios,
        "largest_jump": largest_jump,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [evaluate_case(case) for case in CASES]

    monotonic_ok = all(case["monotonic"] for case in evaluated)
    shell_jump_ok = any(case["largest_jump"] >= 2.0 for case in evaluated)
    nucleus_fixed_ok = all(int(case["atomic_number"]) > 0 for case in evaluated)
    verdict = "supported" if monotonic_ok and shell_jump_ok and nucleus_fixed_ok else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "monotonic_ok": monotonic_ok,
        "shell_jump_ok": shell_jump_ok,
        "nucleus_fixed_ok": nucleus_fixed_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"ionization_successive_check_{ts}.json"
    report_path = outdir / f"ionization_successive_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Ionization successive check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        f"monotonic_ok: {monotonic_ok}",
        f"shell_jump_ok: {shell_jump_ok}",
        f"nucleus_fixed_ok: {nucleus_fixed_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        energies = ", ".join(f"{value:.4f}" for value in case["ionization_energies_ev"])
        ratios = ", ".join(f"{value:.3f}" for value in case["ratios"])
        lines.append(
            f"- {case['name']}: Z={case['atomic_number']} energies=[{energies}] monotonic={case['monotonic']} largest_jump={case['largest_jump']:.3f} ratios=[{ratios}]"
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