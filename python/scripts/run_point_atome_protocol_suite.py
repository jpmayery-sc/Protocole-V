"""Run the point_atome protocol chain and summarize the result."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from run_atom_basics_suite import run_suite as run_atom_basics_suite
from run_heavy_border_suite import run_suite as run_heavy_border_suite
from run_omega_structure_suite import run_suite as run_omega_structure_suite
from run_regime_physics_suite import run_suite as run_regime_physics_suite
from run_saturation_suite import run_suite as run_saturation_suite


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_summary() -> dict:
    suite_specs = [
        ("saturation_magnetic", run_saturation_suite),
        ("omega_structure", run_omega_structure_suite),
        ("heavy_border", run_heavy_border_suite),
        ("atom_basics", run_atom_basics_suite),
        ("regime_physics", run_regime_physics_suite),
    ]

    items = []
    supported = 0

    for label, runner in suite_specs:
        suite_result = runner()
        verdict = suite_result.get("overall_verdict") or suite_result.get("verdict") or "unknown"
        if verdict in {"supported", "conforme strict"}:
            supported += 1
        items.append(
            {
                "label": label,
                "verdict": verdict,
                "json_path": suite_result.get("json_path"),
                "txt_path": suite_result.get("txt_path"),
                "items": suite_result.get("items", []),
            }
        )

    overall_verdict = "supported" if supported == len(items) else ("contradicted" if supported == 0 else "partiel")
    return {
        "suite": "point_atome_protocol",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": supported,
        "total": len(items),
        "items": items,
    }


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"point_atome_protocol_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"point_atome_protocol_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Point Atome protocol suite summary",
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
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"

    summary = build_summary()
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the point_atome protocol chain and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()