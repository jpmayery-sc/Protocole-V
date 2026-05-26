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


def build_summary(result_dir: Path) -> dict[str, object]:
    report_specs = [
        ("v44decomposition_check", "v44_decomposition"),
        ("v44kt_potential_check", "v44_kt_potential"),
        ("v44y_potential_check", "v44_y_potential"),
        ("v44couplings_check", "v44_couplings"),
        ("v44stability_check", "v44_stability"),
        ("v44synthesis_check", "v44_synthesis"),
    ]

    items = []
    supported = 0
    for stem, label in report_specs:
        report_path = latest_report(result_dir, stem)
        report = json.loads(report_path.read_text(encoding="utf-8"))
        verdict = report.get("verdict") or "unknown"
        txt_path = report.get("txt_path") or str(report_path.with_suffix(".txt"))
        if verdict == "supported":
            supported += 1
        items.append({"label": label, "verdict": verdict, "json_path": str(report_path), "txt_path": str(txt_path)})

    global_verdict = "supported" if supported == len(items) else ("rejected" if supported == 0 else "partially_supported")
    return {
        "suite": "v44potential_suite",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "v44_global_verdict": global_verdict,
        "supported_count": supported,
        "total": len(items),
        "items": items,
    }


def write_summary(summary: dict[str, object], result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"v44potential_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"v44potential_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")

    lines = [
        "V44 potential suite summary",
        f"timestamp: {timestamp}",
        f"v44_global_verdict: {summary['v44_global_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        "",
        "Items:",
    ]
    items = summary["items"]  # type: ignore[assignment]
    for item in items:
        lines.append(f"- {item['label']}: {item['verdict']} -> {item['json_path']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_suite(output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    scripts_dir = root / "python" / "scripts"
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    report_dir = result_dir / "v44_potential"

    commands = [
        [sys.executable, str(scripts_dir / "v44decomposition_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "v44kt_potential_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "v44y_potential_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "v44couplings_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "v44stability_check.py"), "--output-dir", str(result_dir)],
        [sys.executable, str(scripts_dir / "v44synthesis_check.py"), "--output-dir", str(result_dir)],
    ]

    for command in commands:
        run_script(command)

    summary = build_summary(report_dir)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V44 potential suite and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()