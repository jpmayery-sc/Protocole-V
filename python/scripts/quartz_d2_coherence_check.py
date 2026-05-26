"""Validate the quartz-as-D2-coherence hypothesis.

The check uses a small geometric proxy inspired by the triangle scan utilities.
Quartz motifs are expected to sit in a coherent D2-like band: common gcd,
small torsion, and a moderate aspect ratio. A control set is used to make the
test falsifiable.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


QUARTZ_MOTIFS = [
    {"name": "q1", "m": 30, "n": 42, "k": 54},
    {"name": "q2", "m": 36, "n": 48, "k": 60},
    {"name": "q3", "m": 42, "n": 56, "k": 70},
    {"name": "q4", "m": 45, "n": 60, "k": 75},
]

CONTROL_MOTIFS = [
    {"name": "c1", "m": 31, "n": 44, "k": 58},
    {"name": "c2", "m": 33, "n": 47, "k": 69},
    {"name": "c3", "m": 35, "n": 51, "k": 82},
    {"name": "c4", "m": 29, "n": 46, "k": 93},
]

MAX_TORSION = 1
MIN_ASPECT = 1.2
MAX_ASPECT = 2.1


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def coherent_gcd(m: int, n: int, k: int) -> bool:
    gmn = math.gcd(m, n)
    gnk = math.gcd(n, k)
    gmk = math.gcd(m, k)
    return gmn == gnk == gmk


def q_t(m: int, n: int, k: int) -> tuple[int, int]:
    d1 = n - m
    d2 = k - n
    diff = d2 - d1
    q = 0
    if diff > 0:
        q = 1
    elif diff < 0:
        q = -1
    return q, abs(diff)


def aspect(m: int, n: int, k: int) -> float:
    return k / m


def mass_geo(m: int, n: int, k: int) -> float:
    _, torsion = q_t(m, n, k)
    s = 0.5 * (m + n + k)
    area_sq = s * (s - m) * (s - n) * (s - k)
    area = math.sqrt(area_sq) if area_sq > 0 else 0.0
    return area / (1.0 + torsion * torsion)


def evaluate_motif(motif: dict) -> dict:
    m = int(motif["m"])
    n = int(motif["n"])
    k = int(motif["k"])
    q, torsion = q_t(m, n, k)
    a = aspect(m, n, k)
    coherent = coherent_gcd(m, n, k)
    in_band = coherent and torsion <= MAX_TORSION and MIN_ASPECT <= a <= MAX_ASPECT and q >= 0
    return {
        **motif,
        "q": q,
        "torsion": torsion,
        "aspect": a,
        "mass_geo": mass_geo(m, n, k),
        "coherent": coherent,
        "in_band": in_band,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    quartz_results = [evaluate_motif(motif) for motif in QUARTZ_MOTIFS]
    control_results = [evaluate_motif(motif) for motif in CONTROL_MOTIFS]

    quartz_ok = all(item["in_band"] for item in quartz_results)
    control_ok = not any(item["in_band"] for item in control_results)
    separation_ok = quartz_ok and control_ok
    verdict = "supported" if separation_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "quartz_ok": quartz_ok,
        "control_ok": control_ok,
        "separation_ok": separation_ok,
        "quartz_results": quartz_results,
        "control_results": control_results,
        "thresholds": {
            "max_torsion": MAX_TORSION,
            "min_aspect": MIN_ASPECT,
            "max_aspect": MAX_ASPECT,
        },
    }

    json_path = outdir / f"quartz_d2_coherence_check_{timestamp}.json"
    txt_path = outdir / f"quartz_d2_coherence_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Quartz D2 coherence check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"quartz_ok: {quartz_ok}",
        f"control_ok: {control_ok}",
        f"separation_ok: {separation_ok}",
        "",
        "Quartz motifs:",
    ]
    for item in quartz_results:
        lines.append(
            f"- {item['name']}: m={item['m']} n={item['n']} k={item['k']} q={item['q']} torsion={item['torsion']} aspect={item['aspect']:.3f} in_band={item['in_band']}"
        )
    lines.extend(["", "Control motifs:"])
    for item in control_results:
        lines.append(
            f"- {item['name']}: m={item['m']} n={item['n']} k={item['k']} q={item['q']} torsion={item['torsion']} aspect={item['aspect']:.3f} in_band={item['in_band']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the quartz D2 coherence hypothesis.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()