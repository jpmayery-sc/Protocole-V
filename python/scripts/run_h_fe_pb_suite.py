"""Run the H / Fe / Pb campaign checks and summarize the result."""
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


def run_script(command: list[str], cwd: Path) -> None:
    print(f"Running: {Path(command[1]).name}")
    subprocess.run(command, check=True, cwd=str(cwd))


def build_summary(result_dir: Path) -> dict:
    report_specs = [
        ("h_fe_pb_check", "h_fe_pb"),
        ("electron_validation_results", "electron_validation"),
        ("sweep_all", "sweep_min_neutron"),
    ]

    items = []
    supported = 0
    for stem, label in report_specs:
        report_path = latest_report(result_dir, stem)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        verdict = report.get("verdict") or report.get("overall_verdict") or "supported"
        txt_path = report.get("report_path") or report.get("txt_path") or str(report_path.with_suffix(".txt"))
        if verdict in {"supported", "conforme strict"}:
            supported += 1
        items.append(
            {
                "label": label,
                "verdict": verdict,
                "json_path": str(report_path),
                "txt_path": txt_path,
            }
        )

    overall_verdict = "supported" if supported == len(items) else ("contradicted" if supported == 0 else "partiel")

    return {
        "suite": "h_fe_pb",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": supported,
        "total": len(items),
        "items": items,
    }


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"h_fe_pb_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"h_fe_pb_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "H / Fe / Pb suite summary",
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
    python_dir = root / "python"
    scripts_dir = python_dir / "scripts"
    result_dir = Path(output_dir) if output_dir is not None else python_dir / "results" / "h_fe_pb"

    commands = [
        [sys.executable, str(scripts_dir / "validate_electron_document.py")],
        [sys.executable, str(scripts_dir / "sweep_min_neutron.py")],
        [sys.executable, str(scripts_dir / "plot_electron_validation.py")],
        [sys.executable, str(scripts_dir / "h_fe_pb_check.py"), "--output-dir", str(result_dir)],
    ]

    for command in commands:
        run_script(command, cwd=python_dir)

    summary = build_summary(python_dir / "results")
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the H / Fe / Pb campaign checks and summarize them.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()