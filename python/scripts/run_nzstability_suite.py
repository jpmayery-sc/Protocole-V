"""Run the nuclear-stability check and summarize the result."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def latest_report(result_dir: Path, stem: str) -> Path:
    matches = sorted(result_dir.glob(f"{stem}_*.json"))
    if not matches:
        raise FileNotFoundError(f"No report found for {stem} in {result_dir}")
    return matches[-1]


def run_script(command: list[str]) -> None:
    print(f"Running: {Path(command[1]).name}")
    subprocess.run(command, check=True)


def build_summary(result_dir: Path) -> dict:
    report_path = latest_report(result_dir, "nzstability_check")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    verdict = report.get("verdict") or "unknown"

    return {
        "suite": "nzstability",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": verdict if verdict == "supported" else "contradicted",
        "supported_count": 1 if verdict == "supported" else 0,
        "total": 1,
        "items": [
            {
                "label": "nzstability",
                "verdict": verdict,
                "json_path": str(report_path),
                "txt_path": report.get("report_path") or str(report_path.with_suffix(".txt")),
                "hypothesis": report.get("hypothesis") or "nuclear stability follows a curve with an optimum in N/Z and a peak near Fe-56",
            }
        ],
    }


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"nzstability_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"nzstability_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Nuclear stability suite summary",
        f"timestamp: {timestamp}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        "",
        "Items:",
    ]
    for item in summary["items"]:
        lines.append(f"- {item['label']}: {item['verdict']} -> {item['json_path']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_suite(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    scripts_dir = root / "python" / "scripts"
    result_dir = Path(output_dir) if output_dir is not None else root / "python" / "results" / "nzstability"

    command = [sys.executable, str(scripts_dir / "nzstability_check.py"), "--output-dir", str(result_dir)]
    run_script(command)

    summary = build_summary(result_dir)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the nuclear-stability check and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()