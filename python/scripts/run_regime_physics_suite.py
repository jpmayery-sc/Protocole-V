"""Run the regime-physics checks and summarize the results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from regime_physics_common import latest_report, workspace_root, write_report


def run_script(command: list[str]) -> None:
    print(f"Running: {Path(command[1]).name}")
    subprocess.run(command, check=True)


def build_summary(result_dir: Path) -> dict:
    report_specs = [
        ("regime_atomique_check", "atomique"),
        ("regime_metal_check", "metal"),
        ("regime_lanthanide_check", "lanthanide"),
        ("regime_dense_check", "dense"),
        ("regime_flow_check", "flow"),
    ]

    items = []
    supported = 0
    for stem, label in report_specs:
        report_path = latest_report(result_dir, stem)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        verdict = report.get("verdict", "unknown")
        if verdict == "supported":
            supported += 1
        items.append(
            {
                "label": label,
                "verdict": verdict,
                "json_path": str(report_path),
                "txt_path": report.get("txt_path", str(report_path.with_suffix(".txt"))),
                "hypothesis": report.get("hypothesis"),
            }
        )

    overall_verdict = "supported" if supported == len(items) else ("contradicted" if supported == 0 else "partiel")
    return {
        "suite": "regime_physics",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": supported,
        "total": len(items),
        "items": items,
    }


def run_suite(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    scripts_dir = root / "python" / "scripts"
    result_dir = Path(output_dir) if output_dir is not None else root / "python" / "results" / "regime_physics"

    commands = [
        [sys.executable, str(scripts_dir / "regime_atomique_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "regime_metal_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "regime_lanthanide_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "regime_dense_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "regime_flow_check.py"), "--output-dir", str(result_dir)],
    ]

    for command in commands:
        run_script(command)

    summary = build_summary(result_dir)
    json_path, txt_path = write_report("Regime physics suite summary", "regime_physics_suite_summary", summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the regime-physics checks and summarize them.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()