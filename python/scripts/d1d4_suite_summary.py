"""Summarize the D1 / D4 regime checks in one report.

This helper scans the regime-specific outputs, picks the latest report for each
regime, and writes a compact suite summary in JSON and TXT form.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path


RESULT_PATTERN = re.compile(r"d1d4_(atomic|metallic|dense)_regime_check_(\d{8}-\d{6}Z)\.json$")


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def find_latest_result_files(results_dir: Path) -> dict[str, Path]:
    latest: dict[str, tuple[str, Path]] = {}
    for path in results_dir.glob("d1d4_*_regime_check_*.json"):
        match = RESULT_PATTERN.search(path.name)
        if not match:
            continue
        regime = match.group(1)
        timestamp = match.group(2)
        if regime not in latest or timestamp > latest[regime][0]:
            latest[regime] = (timestamp, path)
    return {regime: item[1] for regime, item in latest.items()}


def load_result(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def build_summary(regime_files: dict[str, Path]) -> dict:
    regime_results = {regime: load_result(path) for regime, path in regime_files.items()}
    ordered_regimes = ["atomic", "metallic", "dense"]
    supported = [regime for regime in ordered_regimes if regime_results.get(regime, {}).get("verdict") == "supported"]

    return {
        "suite": "D1/D4",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "supported_count": len(supported),
        "total": len(ordered_regimes),
        "overall_verdict": "supported" if len(supported) == len(ordered_regimes) else "partial",
        "regimes": [
            {
                "regime": regime,
                "verdict": regime_results[regime]["verdict"],
                "json_path": regime_results[regime]["json_path"],
                "txt_path": regime_results[regime]["txt_path"],
                "hypothesis": regime_results[regime]["hypothesis"],
            }
            for regime in ordered_regimes
            if regime in regime_results
        ],
    }


def write_summary(summary: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"d1d4_suite_summary_{timestamp}.json"
    txt_path = output_dir / f"d1d4_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "D1/D4 suite summary",
        f"timestamp: {timestamp}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        "",
        "Regimes:",
    ]
    for item in summary["regimes"]:
        lines.append(f"- {item['regime']}: {item['verdict']} -> {item['json_path']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_summary(output_dir: str | Path | None = None, input_dir: str | Path | None = None) -> dict:
    root = project_root()
    results_dir = Path(input_dir) if input_dir is not None else root / "results" / "d1d4"
    outdir = Path(output_dir) if output_dir is not None else results_dir

    regime_files = find_latest_result_files(results_dir)
    summary = build_summary(regime_files)
    json_path, txt_path = write_summary(summary, outdir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    summary["source_files"] = {regime: str(path) for regime, path in regime_files.items()}
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Summarize the D1 / D4 regime checks.")
    parser.add_argument("--input-dir", default=None, help="Directory containing the regime JSON reports")
    parser.add_argument("--output-dir", default=None, help="Directory for the summary report")
    args = parser.parse_args()

    result = run_summary(args.output_dir, args.input_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()