"""Check the V5-N alpha(n) torsion-order port."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASES = [
    {"n": 2, "label": "squeezing", "rn": 1.09, "tsqz_us": 400.0},
    {"n": 3, "label": "trisqueezing", "rn": 0.19, "tsqz_us": 600.0},
    {"n": 4, "label": "quadsqueezing", "rn": 0.054, "tsqz_us": 600.0},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_torsion_order() -> dict:
    cases = []
    for case in CASES:
        kappa_n = case["rn"] / case["tsqz_us"]
        cases.append({**case, "kappa_n": kappa_n})

    kappa_2 = cases[0]["kappa_n"]
    kappa_3 = cases[1]["kappa_n"]
    kappa_4 = cases[2]["kappa_n"]

    ratio3over2 = kappa_3 / kappa_2
    ratio4over3 = kappa_4 / kappa_3
    ratio4over2 = kappa_4 / kappa_2

    trend_ok = kappa_2 > kappa_3 > kappa_4
    controlled_decay_ok = ratio3over2 > 0.05 and ratio4over3 > 0.05
    order_spread_ok = ratio4over2 > 0.01
    verdict = "conforme" if trend_ok and controlled_decay_ok and order_spread_ok else ("partiel" if trend_ok else "rejette")

    return {
        "cases": cases,
        "kappa_2": kappa_2,
        "kappa_3": kappa_3,
        "kappa_4": kappa_4,
        "ratio3over2": ratio3over2,
        "ratio4over3": ratio4over3,
        "ratio4over2": ratio4over2,
        "trend_ok": trend_ok,
        "controlled_decay_ok": controlled_decay_ok,
        "order_spread_ok": order_spread_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_torsion_order()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la force effective de la porte alpha reste controlable avec l'ordre n",
        "case_control": "n = 2 (squeezing), 3 (trisqueezing), 4 (quadsqueezing)",
        "observable": "pentes kappan = rn / tsqzn",
        "expected": "kappa_n decroissante mais non catastrophique avec n",
        "measured": {
            "kappa_2": result["kappa_2"],
            "kappa_3": result["kappa_3"],
            "kappa_4": result["kappa_4"],
            "ratio3over2": result["ratio3over2"],
            "ratio4over3": result["ratio4over3"],
            "ratio4over2": result["ratio4over2"],
        },
        "trend_ok": result["trend_ok"],
        "controlled_decay_ok": result["controlled_decay_ok"],
        "order_spread_ok": result["order_spread_ok"],
        "verdict": result["verdict"],
        "reference": "squeezing/trisqueezing/quadsqueezing trapped ion",
    }

    json_path = outdir / f"alphatorsionorder_check_{timestamp}.json"
    txt_path = outdir / f"alphatorsionorder_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Alpha torsion-order check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"kappa_2: {result['kappa_2']:.15e}",
        f"kappa_3: {result['kappa_3']:.15e}",
        f"kappa_4: {result['kappa_4']:.15e}",
        f"ratio3over2: {result['ratio3over2']:.15f}",
        f"ratio4over3: {result['ratio4over3']:.15f}",
        f"ratio4over2: {result['ratio4over2']:.15f}",
        f"trend_ok: {result['trend_ok']}",
        f"controlled_decay_ok: {result['controlled_decay_ok']}",
        f"order_spread_ok: {result['order_spread_ok']}",
        "",
        "Cases:",
    ]
    for case in result["cases"]:
        lines.append(
            f"- n={case['n']} {case['label']}: rn={case['rn']} tsqz_us={case['tsqz_us']} kappa_n={case['kappa_n']:.15e}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V5-N alpha(n) torsion-order port.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()