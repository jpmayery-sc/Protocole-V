"""Validate the three-phase current block with deterministic waveforms.

The check uses ideal sinusoidal phases for an equilibrated system, a mild
amplitude mismatch for a desbalanced system, and a cut phase for a hard fault.
It verifies neutral current, power stability, and symmetry loss.
"""
from __future__ import annotations

import argparse
import json
import math
import statistics
import time
from pathlib import Path


SAMPLES = 720
TWO_PI = 2.0 * math.pi


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def make_waveform(amplitudes: tuple[float, float, float], phase_offsets: tuple[float, float, float]) -> list[tuple[float, float, float]]:
    points: list[tuple[float, float, float]] = []
    for index in range(SAMPLES):
        angle = TWO_PI * index / SAMPLES
        ia = amplitudes[0] * math.sin(angle + phase_offsets[0])
        ib = amplitudes[1] * math.sin(angle + phase_offsets[1])
        ic = amplitudes[2] * math.sin(angle + phase_offsets[2])
        points.append((ia, ib, ic))
    return points


def rms(values: list[float]) -> float:
    return math.sqrt(sum(value * value for value in values) / max(len(values), 1))


def analyze_case(name: str, amplitudes: tuple[float, float, float], phase_offsets: tuple[float, float, float]) -> dict:
    points = make_waveform(amplitudes, phase_offsets)
    sums = [ia + ib + ic for ia, ib, ic in points]
    powers = [ia * ia + ib * ib + ic * ic for ia, ib, ic in points]
    phase_rms = [rms([sample[index] for sample in points]) for index in range(3)]

    power_mean = statistics.mean(powers)
    power_stdev = statistics.pstdev(powers)
    sum_rms = rms(sums)
    neutral_rms = sum_rms
    phase_shift_degrees = [offset * 180.0 / math.pi for offset in phase_offsets]

    return {
        "name": name,
        "amplitudes": list(amplitudes),
        "phase_offsets_deg": phase_shift_degrees,
        "phase_rms": phase_rms,
        "sum_rms": sum_rms,
        "neutral_rms": neutral_rms,
        "power_mean": power_mean,
        "power_stdev": power_stdev,
        "power_cv": power_stdev / power_mean if power_mean else float("nan"),
    }


def classify_cases() -> dict:
    balanced = analyze_case("balanced", (1.0, 1.0, 1.0), (0.0, -2.0 * math.pi / 3.0, 2.0 * math.pi / 3.0))
    unbalanced = analyze_case("unbalanced", (1.0, 0.85, 1.15), (0.0, -2.0 * math.pi / 3.0, 2.0 * math.pi / 3.0))
    cut = analyze_case("phase_cut", (1.0, 1.0, 0.0), (0.0, -2.0 * math.pi / 3.0, 2.0 * math.pi / 3.0))

    balanced_sum_ok = balanced["sum_rms"] < 1.0e-12
    balanced_power_ok = balanced["power_cv"] < 1.0e-12
    unbalanced_neutral_ok = unbalanced["neutral_rms"] > 0.05
    unbalanced_power_ok = unbalanced["power_cv"] > 0.01
    cut_symmetry_ok = cut["phase_rms"][2] < 0.05 and cut["neutral_rms"] > unbalanced["neutral_rms"]
    phase_offsets_ok = all(
        abs(observed - expected) < 1.0e-9
        for observed, expected in zip(balanced["phase_offsets_deg"], [0.0, -120.0, 120.0])
    )

    overall_ok = all([balanced_sum_ok, balanced_power_ok, unbalanced_neutral_ok, unbalanced_power_ok, cut_symmetry_ok, phase_offsets_ok])

    return {
        "verdict": "supported" if overall_ok else "contradicted",
        "balanced_sum_ok": balanced_sum_ok,
        "balanced_power_ok": balanced_power_ok,
        "unbalanced_neutral_ok": unbalanced_neutral_ok,
        "unbalanced_power_ok": unbalanced_power_ok,
        "cut_symmetry_ok": cut_symmetry_ok,
        "phase_offsets_ok": phase_offsets_ok,
        "cases": {
            "balanced": balanced,
            "unbalanced": unbalanced,
            "phase_cut": cut,
        },
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    data = classify_cases()

    json_path = outdir / f"three_phase_current_check_{ts}.json"
    txt_path = outdir / f"three_phase_current_check_{ts}.txt"
    payload = {"timestamp": ts, **data, "samples": SAMPLES}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Three-phase current check",
        f"timestamp: {ts}",
        f"verdict: {data['verdict']}",
        f"balanced_sum_ok: {data['balanced_sum_ok']}",
        f"balanced_power_ok: {data['balanced_power_ok']}",
        f"unbalanced_neutral_ok: {data['unbalanced_neutral_ok']}",
        f"unbalanced_power_ok: {data['unbalanced_power_ok']}",
        f"cut_symmetry_ok: {data['cut_symmetry_ok']}",
        f"phase_offsets_ok: {data['phase_offsets_ok']}",
        "",
        "Cases:",
    ]
    for name, case in data["cases"].items():
        lines.append(
            f"- {name}: sum_rms={case['sum_rms']:.6e} neutral_rms={case['neutral_rms']:.6e} power_cv={case['power_cv']:.6e} phase_rms={case['phase_rms']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["report_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the three-phase current block.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()