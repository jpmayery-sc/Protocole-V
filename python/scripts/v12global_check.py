"""Aggregate the V12 falsification blocks into a global verdict."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v12absolute_check import evaluate_absolute_bounds
from v12alpha_check import evaluate_alpha_bounds
from v12fine_check import evaluate_fine_bounds


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def evaluate_global_falsification() -> dict:
    absolute_result = evaluate_absolute_bounds()
    alpha_result = evaluate_alpha_bounds()
    fine_result = evaluate_fine_bounds()

    items = [
        {"label": "v12_absolute", "verdict": absolute_result["verdict"], "details": absolute_result},
        {"label": "v12_alpha", "verdict": alpha_result["verdict"], "details": alpha_result},
        {"label": "v12_fine", "verdict": fine_result["verdict"], "details": fine_result},
    ]

    supported_count = sum(1 for item in items if item["verdict"] == "conforme")
    partial_count = sum(1 for item in items if item["verdict"] == "partiel")
    falsified_count = sum(1 for item in items if item["verdict"] == "falsifie")

    if falsified_count > 0:
        overall_verdict = "falsified"
    elif partial_count > 0:
        overall_verdict = "partial"
    else:
        overall_verdict = "supported"

    return {
        "items": items,
        "supported_count": supported_count,
        "partial_count": partial_count,
        "falsified_count": falsified_count,
        "overall_verdict": overall_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_global_falsification()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "V12 rejects the model if any falsification block fails its conservative bounds",
        "case_control": "absolute, alpha, fine",
        "observable": "V12 suite verdicts",
        "expected": "supported if all conform, partial if only borderline, falsified if any block is clearly out of bounds",
        "measured": {
            "supported_count": result["supported_count"],
            "partial_count": result["partial_count"],
            "falsified_count": result["falsified_count"],
        },
        "items": [{"label": item["label"], "verdict": item["verdict"]} for item in result["items"]],
        "verdict": result["overall_verdict"],
        "reference": "V12 absolute, alpha and fine blocks",
    }

    json_path = outdir / f"v12global_check_{timestamp}.json"
    txt_path = outdir / f"v12global_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V12 global falsification check",
        f"timestamp: {timestamp}",
        f"verdict: {result['overall_verdict']}",
        f"supported_count: {result['supported_count']}",
        f"partial_count: {result['partial_count']}",
        f"falsified_count: {result['falsified_count']}",
        "",
        "Blocks:",
    ]
    for item in result["items"]:
        lines.append(f"- {item['label']}: {item['verdict']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Aggregate the V12 falsification blocks into a global verdict.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()