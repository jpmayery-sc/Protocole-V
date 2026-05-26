"""Run the official D1/D2 inter-family suite B and summarize the result."""
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
    report_path = latest_report(result_dir, "official_d1d2_b_tests")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    verdict = report.get("verdict") or report.get("overall_verdict") or "unknown"

    items = []
    for test in report.get("tests", []):
        items.append(
            {
                "label": test.get("name") or test.get("id") or "test",
                "verdict": test.get("verdict", "unknown"),
                "details": test,
            }
        )

    return {
        "suite": "official_d1d2_b",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": verdict,
        "supported_count": sum(1 for item in items if item["verdict"] == "supported"),
        "total": len(items),
        "items": [
            {
                "label": item["label"],
                "verdict": item["verdict"],
                "json_path": str(report_path),
                "txt_path": report.get("txt_path") or str(report_path.with_suffix(".txt")),
            }
            for item in items
        ],
        "hypothesis": "inter-family D1/D2 comparisons should reveal regime separation rather than a universal collapse",
        "negative_control": True,
    }


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"official_d1d2_b_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"official_d1d2_b_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Official D1/D2 suite B summary",
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
    result_dir = Path(output_dir) if output_dir is not None else root / "python" / "results" / "d1d2_official"

    command = [sys.executable, str(scripts_dir / "d1d2_official_b_tests.py")]
    run_script(command)

    summary = build_summary(result_dir)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the official D1/D2 suite B and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()