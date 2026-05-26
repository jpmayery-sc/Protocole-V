"""Validate atomic neutrality and simple ionization examples.

The check is intentionally small and deterministic so it can be run from a
notebook or from the command line without external data.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {"name": "H", "kind": "neutral", "protons": 1, "electrons": 1},
    {"name": "O", "kind": "neutral", "protons": 8, "electrons": 8},
    {"name": "Fe", "kind": "neutral", "protons": 26, "electrons": 26},
    {"name": "U", "kind": "neutral", "protons": 92, "electrons": 92},
    {"name": "Fe2+", "kind": "ion", "protons": 26, "electrons": 24},
    {"name": "Fe3+", "kind": "ion", "protons": 26, "electrons": 23},
    {"name": "O2-", "kind": "ion", "protons": 8, "electrons": 10},
    {"name": "Na+", "kind": "ion", "protons": 11, "electrons": 10},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def classify_case(case: dict) -> dict:
    protons = int(case["protons"])
    electrons = int(case["electrons"])
    charge = protons - electrons
    is_neutral = charge == 0
    expected_neutral = case["kind"] == "neutral"
    ok = is_neutral if expected_neutral else not is_neutral
    return {
        **case,
        "charge": charge,
        "is_neutral": is_neutral,
        "expected_neutral": expected_neutral,
        "ok": ok,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    evaluated = [classify_case(case) for case in CASES]

    neutral_cases = [case for case in evaluated if case["kind"] == "neutral"]
    ion_cases = [case for case in evaluated if case["kind"] == "ion"]

    neutral_ok = all(case["ok"] for case in neutral_cases)
    ion_ok = all(case["ok"] for case in ion_cases)
    verdict = "supported" if neutral_ok and ion_ok else "contradicted"

    data = {
        "timestamp": ts,
        "verdict": verdict,
        "neutral_ok": neutral_ok,
        "ion_ok": ion_ok,
        "cases": evaluated,
    }

    json_path = outdir / f"neutral_atom_check_{ts}.json"
    report_path = outdir / f"neutral_atom_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Neutral atom check",
        f"timestamp: {ts}",
        f"verdict: {verdict}",
        f"neutral_ok: {neutral_ok}",
        f"ion_ok: {ion_ok}",
        "",
        "Cases:",
    ]
    for case in evaluated:
        lines.append(
            f"- {case['name']}: p={case['protons']} e={case['electrons']} charge={case['charge']} ok={case['ok']}"
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